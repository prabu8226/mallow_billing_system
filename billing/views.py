from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import Product, Bill, BillItem
import threading
import json
from math import floor
from django.db import transaction

from django.core.mail import EmailMessage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def index(request):
    products = Product.objects.all()
    for i in products:
        print(i.available_stocks)
    denominations = [500, 50, 20, 10, 5, 2, 1]
    return render(request, 'billing/index.html', {
        'products': products,
        'denominations': denominations
    })



def calculate_denominations(balance, available_denominations):
    result = {}
    sorted_denominations = sorted([int(k) for k in available_denominations.keys()], reverse=True)
    
    remaining_balance = balance
    print(remaining_balance,"dkjbf")
    
    for denom in sorted_denominations:
        if remaining_balance <= 0:
            break
            
        count_needed = int(remaining_balance // denom)
        count_available = available_denominations.get(denom, 0)
        
        take = min(count_needed, count_available)
        
        if take > 0:
            result[denom] = take
            remaining_balance -= (take * denom)
            
    if remaining_balance > 0:
        return result, remaining_balance
    
    return result, 0

def generate_bill(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        cash_paid = float(request.POST.get('cash_paid'))
        
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')

        shop_denominations = {}
        for denom in [500, 50, 20, 10, 5, 2, 1]:
            count = request.POST.get(f'denom_{denom}', 0)
            shop_denominations[denom] = int(count) if count else 0

        total_without_tax = 0.0
        total_tax = 0.0
        
        bill = Bill(customer_email=email)
        bill.save()
        
        bill_items_data = []

        for p_id, qty in zip(product_ids, quantities):
            if not p_id or not qty:
                continue
            
            try:
                product = Product.objects.get(product_id=p_id)
                qty = int(qty)
                
                if product.available_stocks < qty:
                    messages.error(request, f"Insufficient stock for {product.name} (ID: {p_id}). Available: {product.available_stocks}")
                    bill.delete()
                    return redirect('index')

                tax_amount = (product.price * product.tax_percentage / 100) * qty
                
                total_without_tax += (product.price * qty)
                total_tax += tax_amount
               
                # Create BillItem
                bill_item = BillItem(
                    bill=bill,
                    product=product,
                    product_name=product.name,
                    quantity=qty,
                    unit_price=product.price,
                    tax_percentage=product.tax_percentage
                )
                bill_item.save()
                product.available_stocks -= qty
                product.save()
                
                bill_items_data.append(bill_item)
                
            except Product.DoesNotExist:
                messages.error(request, f"Product ID {p_id} not found.")
                bill.delete()
                return redirect('index')
            except ValueError:
                 messages.error(request, f"Invalid quantity for Product ID {p_id}.")
                 bill.delete()
                 return redirect('index')

        net_price = total_without_tax + total_tax

        
        rounded_net_price = floor(net_price)
        balance_payable = cash_paid - rounded_net_price
        
        if balance_payable < 0:
             messages.error(request, f"Insufficient cash paid. Need {rounded_net_price}, paid {cash_paid}")
            
             bill.delete()
             return redirect('index')

        breakdown, remainder = calculate_denominations(balance_payable, shop_denominations)
        
        bill.total_amount_without_tax = total_without_tax
        bill.total_tax_payable = total_tax
        bill.net_price = net_price
        bill.amount_paid = cash_paid
        bill.balance_amount = balance_payable
        bill.balance_denomination_breakdown = breakdown
        bill.save()
        

        
        context = {
            'bill': bill,
            'items': bill_items_data,
            'rounded_net_price': rounded_net_price,
            'breakdown': breakdown,
            'remainder': remainder
        }

        # Send email asynchronously
        email_thread = threading.Thread(target=send_bill_email, args=(bill, bill_items_data))
        email_thread.start()
        
        return render(request, 'billing/bill.html', context)
    
    return redirect('index')

def send_bill_email(bill, items):
    subject = f"Invoice for Bill #{bill.id}"
    message = f"Dear Customer,\n\nThank you for your purchase.\n\n"
    message += f"Bill ID: {bill.id}\n"
    message += f"Date: {bill.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    message += "Items Purchased:\n"
    
    for item in items:
        message += f"- {item.product_name} (Qty: {item.quantity}) - {item.total_price:.2f}\n"
        
    message += f"\nTotal Amount: {bill.net_price:.2f}\n"
    message += f"Amount Paid: {bill.amount_paid:.2f}\n"
    message += f"Balance Returned: {bill.balance_amount:.2f}\n"
    
    if bill.balance_denomination_breakdown:
        message += "\nChange Breakdown:\n"
        for denom, count in bill.balance_denomination_breakdown.items():
            message += f"{denom} : {count}\n"

    message += "\nThank you for shopping with us!"
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [bill.customer_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending email: {e}")

def history(request):
    bills = Bill.objects.all().order_by('-created_at')
    return render(request, 'billing/history.html', {'bills': bills})

def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    items = bill.items.all()
    net_price = bill.net_price
    rounded_net_price = floor(net_price)
    
    return render(request, 'billing/bill_detail.html', {
        'bill': bill,
        'items': items,
        'rounded_net_price': rounded_net_price,
        'breakdown': bill.balance_denomination_breakdown
    })
