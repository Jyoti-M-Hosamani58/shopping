import json
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.http import JsonResponse, HttpResponse,HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse

from shopping_app.models import Login,Items, Sales, Return


from .models import Items
import random
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.utils.dateparse import parse_date

from django.views.generic import TemplateView
class OfflineView(TemplateView):
    template_name = 'offline.html'  #


# Create your views here.
def admin_home(request):
    return render(request,'admin_home.html')

def staff_home(request):
    return render(request,'staff_home.html')

def login(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        request.session['username']=username
        ucount=Login.objects.filter(username=username).count()
        if ucount>=1:
            udata = Login.objects.get(username=username)
            upass = udata.password
            utype=udata.utype
            if password == upass:
                request.session['utype'] = utype
                if utype == 'staff':
                    return redirect('staff_home')
                if utype == 'admin':
                    return render(request,'admin_home.html')

            else:
                return render(request,'login.html',{'msg':'Invalid Password'})
        else:
            return render(request,'login.html',{'msg':'Invalid Username'})
    return render(request,'login.html')

def logout(request):
    return render(request,'login.html')


def addItem(request):
    if request.method == 'POST':
        now = datetime.now()
        con_date = now.strftime("%Y-%m-%d")

        # Get form data
        itemname = request.POST.get('itemname')
        price = request.POST.get('price')
        hsncode = request.POST.get('hsncode')
        gst = request.POST.get('gst')
        cgst = request.POST.get('cgst')
        sgst = request.POST.get('sgst')
        stock = request.POST.get('stock')
        barcode_number = request.POST.get('barcode')



        # Create Item instance
        item = Items(
            itemname=itemname,
            price=price,
            hsncode=hsncode,
            gst=gst,
            cgst=cgst,
            sgst=sgst,
            barcode_number=barcode_number,
            stock=stock,
            date=con_date,
            purchasedstock=stock
        )
        item.save()  # This line was missing


        return redirect('addItem')  # Redirect after save

    return render(request, 'addItem.html')


def generate_unique_barcode():
    """Generate a unique 12-digit barcode number."""
    return str(random.randint(100000000000, 999999999999))

def viewItem(request):
    item=Items.objects.all()

    # Get search query from GET parameters
    itemname = request.GET.get('itemname', '')

    # Filter items based on the itemname if it is provided
    if itemname:
        item = Items.objects.filter(itemname__icontains=itemname)  # Adjust 'itemname' if your model has a different field name
    else:
        items = Items.objects.all()
    return render(request,'viewItem.html',{'item':item})


from django.shortcuts import get_object_or_404

def editItem(request, pk):
    # Fetch the item using get_object_or_404 to avoid errors if it doesn't exist
    data = get_object_or_404(Items, barcode_number=pk)
    # Try to fetch the datareport; it's okay if it doesn't exist

    if request.method == "POST":
        # Get updated values from the POST request
        itemname = request.POST.get('itemname')
        hsncode = request.POST.get('hsncode')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        purchasedstock = request.POST.get('purchasedstock')
        gst = request.POST.get('gst')
        cgst = request.POST.get('cgst')
        sgst = request.POST.get('sgst')

        # Update the Items object
        data.itemname = itemname
        data.hsncode = hsncode
        data.price = price
        data.purchasedstock = stock
        data.stock = stock
        data.purchasedstock=purchasedstock
        data.gst = gst
        data.cgst = cgst
        data.sgst = sgst
        data.save()

        # Redirect to a different URL after a successful update
        return redirect('viewItem')

    return render(request, 'editItem.html', {'data': data})


def get_item(request):
    query = request.GET.get('query', '')
    if query:
        itemname = Items.objects.filter(itemname__icontains=query).values_list('itemname', flat=True)
        print('Item Name:', list(itemname))  # Debugging: check the data in the terminal
        return JsonResponse(list(itemname), safe=False)
    return JsonResponse([], safe=False)

def sales(request):
    return render(request,'sales.html')


def get_item_by_barcode(request, barcode):
    try:
        item = Items.objects.get(barcode_number=barcode)
        item_data = {
            "itemname": item.itemname,
            "hsncode": item.hsncode,
            "price": item.price,
            "gst": item.gst,
            "barcode_number": item.barcode_number,
        }
        return JsonResponse({"success": True, "item": item_data})
    except Items.DoesNotExist:
        return JsonResponse({"success": False, "message": "Item not found."})


@csrf_exempt
def save_sales(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")

                uid = request.session.get('username')
                name = Login.objects.get(username=uid)
                username = name.name

                last_invoice = Sales.objects.aggregate(Max('invoiceNo'))['invoiceNo__max']
                invoiceNo = int(last_invoice) + 1 if last_invoice else 10001
                invoice_id = str(invoiceNo)

                phone = request.POST.get('phone')
                payment_mode = request.POST.get('payment')
                name = request.POST.get('name')
                discount = request.POST.get('discount')
                discountAmt = request.POST.get('discountAmt')
                # Get Cash and UPI from the POST request or set to 0 if not provided
                Cash = request.POST.get('Cash', '0')
                UPI = request.POST.get('UPI', '0')

                # Convert to integer, default to 0 if they are empty strings
                Cash = Cash if Cash else 0.0
                UPI = UPI if UPI else 0.0
                items_data = request.POST.get('items')  # Get items as JSON string

                if not items_data:
                    raise ValueError("No items provided in the request.")

                items_data = json.loads(items_data)  # Load items from JSON string

                for item in items_data:
                    item_name = item['itemName']
                    hsn_code = item['hsnCode']
                    price = item['price']
                    quantity = int(item['quantity'])  # Convert quantity to integer
                    gst = item['gst']
                    barcode = item.get('barcode')
                    gst1 = float(item['gst'])  # Ensure gst is treated as float

                    cgst = gst1 / 2
                    sgst = gst1 / 2

                    item_record = Sales(
                        phonenumber=phone,
                        itemname=item_name,
                        hsncode=hsn_code,
                        price=price,
                        quantity=quantity,
                        gst=gst,
                        cgst=cgst,
                        sgst=sgst,
                        date=con_date,
                        username=username,
                        invoiceNo=invoice_id,
                        barcode_number=barcode,
                        payment_mode=payment_mode,
                        cash=Cash,
                        UPI=UPI,
                        discount=discount,
                        discountAmt=discountAmt,
                        status='Sale'
                    )
                    item_record.save()

                    # Update stock in Items model
                    item_obj = Items.objects.get(barcode_number=barcode)
                    if item_obj.stock >= quantity:
                        item_obj.stock -= quantity
                        item_obj.save()
                    else:
                        raise ValueError(f"Insufficient stock for item: {item_name}")

            # Successful save response
            return JsonResponse({'success': True, 'message': 'Sales saved successfully!', 'invoice_no': invoice_id})

        except Exception as e:
            print(f"Error: {str(e)}")  # Print error to terminal for debugging
            return JsonResponse({'success': False, 'message': str(e)})  # Return error response only within the except block

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




from django.shortcuts import  get_object_or_404

from django.db.models import Sum

from django.shortcuts import render
from django.db.models import Sum

def printInvoice(request, invoice_no):
    # Get all sales records related to this invoice number
    items = Sales.objects.filter(invoiceNo=invoice_no)

    # Check if there are items for the invoice
    if not items.exists():
        return render(request, 'printinvoice.html', {
            'invoice_details': None,
            'items': [],
            'total_qty': 0,
            'subtotal': 0.0,
            'cgst_total': 0.0,
            'sgst_total': 0.0,
            'grand_total': 0.0,
            'discounted_total': 0.0,
        })

    # Initialize totals
    total_qty = 0
    subtotal = 0.0
    cgst_total = 0.0
    sgst_total = 0.0
    grand_total = 0.0

    # Calculate totals, GST, and grand total for each item
    for item in items:
        item_price = float(item.price)  # Ensure item.price is a float
        item_quantity = int(item.quantity)  # Ensure item.quantity is an integer
        item_total_price = item_price * item_quantity  # Calculate total price per item

        # Add to total quantity and subtotal
        total_qty += item_quantity
        subtotal += item_total_price  # Add the total price per item to subtotal

        # Calculate GST amounts
        item_gst = float(item.gst)  # Ensure GST is a float
        item_gst_amount = (item_total_price * item_gst) / 100  # Calculate GST amount

        item_cgst = item_gst_amount / 2  # Split GST into CGST and SGST
        item_sgst = item_gst_amount / 2

        cgst_total += item_cgst
        sgst_total += item_sgst

        # Add item total (price * quantity) to grand total
        grand_total += item_total_price

    # Retrieve the discount amount (discountAmt) from the first item (or any other record related to the invoice)
    discount_amount = items.first().discountAmt if hasattr(items.first(), 'discountAmt') else 0.0

    # Calculate discounted total using the discount amount
    discounted_total = grand_total - discount_amount

    # Render the invoice template with all calculated values
    return render(request, 'printinvoice.html', {
        'invoice_details': items.first(),  # Use the first record for invoice details
        'items': items,
        'total_qty': total_qty,
        'subtotal': subtotal,
        'cgst_total': cgst_total,
        'sgst_total': sgst_total,
        'grand_total': grand_total,
        'discounted_total': discounted_total,
    })



from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.utils.dateparse import parse_date

def viewSales(request):
    # Fetch date filter from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Filter sales by date if provided
    sales = Sales.objects.all()
    if from_date:
        sales = sales.filter(date__gte=parse_date(from_date))
    if to_date:
        sales = sales.filter(date__lte=parse_date(to_date))

    # Group sales by invoiceNo and calculate aggregate fields
    sales_summary = {}
    for sale in sales:
        invoice_no = sale.invoiceNo
        if invoice_no not in sales_summary:
            # Initialize summary for each invoice
            sales_summary[invoice_no] = {
                'date': sale.date,
                'payment_mode': sale.payment_mode,
                'cash': sale.cash,
                'UPI': sale.UPI,
                'items': [],
                'grand_qty': 0,
                'grand_print': 0.0,
                'grand_price_with_gst': 0.0,
                'cgst_amount': 0.0,
                'sgst_amount': 0.0,
            }

        # Add item details for each invoice
        sales_summary[invoice_no]['items'].append({
            'itemname': sale.itemname,
            'quantity': sale.quantity,
            'price': sale.price,
        })

        # Convert price to float to avoid type errors and calculate total price for the item
        price = float(sale.price)
        quantity = sale.quantity
        gst = float(sale.gst) if hasattr(sale, 'gst') else 0.0
        item_total = price * quantity  # Total price for the item

        # Update aggregate totals with price * quantity
        sales_summary[invoice_no]['grand_qty'] += quantity
        sales_summary[invoice_no]['grand_print'] += item_total

        # Do not calculate grand_price_with_gst including GST
        # Simply add the item total without GST to grand_price_with_gst
        sales_summary[invoice_no]['grand_price_with_gst'] += item_total

        cgst = gst / 2
        sgst = gst / 2
        sales_summary[invoice_no]['cgst_amount'] += item_total * cgst / 100
        sales_summary[invoice_no]['sgst_amount'] += item_total * sgst / 100

    # Pass sales summary to the template
    return render(request, 'viewSales.html', {'sales_summary': sales_summary})


def returnReport(request):
    # Fetch date filter from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Filter sales by date if provided
    sales = Return.objects.all()
    if from_date:
        sales = sales.filter(date__gte=parse_date(from_date))
    if to_date:
        sales = sales.filter(date__lte=parse_date(to_date))

    # Group sales by invoiceNo and calculate aggregate fields
    sales_summary = {}
    for sale in sales:
        invoice_no = sale.invoiceNo
        if invoice_no not in sales_summary:
            # Initialize summary for each invoice
            sales_summary[invoice_no] = {
                'date': sale.date,
                'items': [],
                'grand_qty': 0,
                'grand_print': 0.0,
                'grand_price_with_gst': 0.0,
                'cgst_amount': 0.0,
                'sgst_amount': 0.0,
            }

        # Add item details for each invoice
        sales_summary[invoice_no]['items'].append({
            'itemname': sale.itemname,
            'quantity': sale.quantity,
            'price':sale.price,
        })

        # Convert price to float to avoid type errors and calculate total price for the item
        price = float(sale.price)
        quantity = sale.quantity
        gst = float(sale.gst) if hasattr(sale, 'gst') else 0.0
        item_total = price * quantity  # Total price for the item

        # Update aggregate totals with price * quantity
        sales_summary[invoice_no]['grand_qty'] += quantity
        sales_summary[invoice_no]['grand_print'] += price * quantity
        sales_summary[invoice_no]['grand_price_with_gst'] += (price * quantity) + ((price * quantity) * gst / 100)

        cgst = gst / 2
        sgst = gst / 2
        sales_summary[invoice_no]['cgst_amount'] += item_total * cgst / 100
        sales_summary[invoice_no]['sgst_amount'] += item_total * sgst / 100
    # Pass sales summary to the template
    return render(request, 'returnReport.html', {'sales_summary': sales_summary})

def returnSale(request):
    return render(request,'returnSale.html')

@csrf_exempt
def save_return(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                now = datetime.now()
                con_date = now.strftime("%Y-%m-%d")

                uid = request.session.get('username')
                name = Login.objects.get(username=uid)
                username = name.name


                phone = request.POST.get('phone')
                invoice_id = request.POST.get('bill')

                items_data = request.POST.get('items')  # Get items as JSON string

                if not items_data:
                    raise ValueError("No items provided in the request.")

                items_data = json.loads(items_data)  # Load items from JSON string

                for item in items_data:
                    item_name = item['itemName']
                    hsn_code = item['hsnCode']
                    price = item['price']
                    quantity = int(item['quantity'])  # Convert quantity to integer
                    gst = item['gst']
                    barcode = item.get('barcode')
                    gst1 = float(item['gst'])  # Ensure gst is treated as float

                    cgst = gst1 / 2
                    sgst = gst1 / 2

                    item_record = Return(
                        phonenumber=phone,
                        itemname=item_name,
                        hsncode=hsn_code,
                        price=price,
                        quantity=quantity,
                        gst=gst,
                        cgst=cgst,
                        sgst=sgst,
                        date=con_date,
                        username=username,
                        invoiceNo=invoice_id,
                        barcode_number=barcode,
                    )
                    item_record.save()



                    # Update stock in Items model by adding back the quantity
                    item_obj = Items.objects.get(barcode_number=barcode)
                    item_obj.stock += quantity  # Increase stock by the returned quantity
                    item_obj.save()

                    # Update status and returned quantity in the Sales model
                    sale_obj = Sales.objects.get(invoiceNo=invoice_id, barcode_number=barcode)
                    sale_obj.status = f"{quantity} quantity returned"
                    sale_obj.save()

            # Successful save response
            return JsonResponse({'success': True, 'message': 'Return saved successfully!', 'invoice_no': invoice_id})

        except Exception as e:
            print(f"Error: {str(e)}")  # Print error to terminal for debugging
            return JsonResponse({'success': False, 'message': str(e)})  # Return error response only within the except block

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

def get_item_barcode_return(request, bill, barcode):
    try:
        item = Sales.objects.get(barcode_number=barcode, invoiceNo=bill)
        item_data = {
            "itemname": item.itemname,
            "hsncode": item.hsncode,
            "price": item.price,
            "gst": item.gst,
            "barcode_number": item.barcode_number,
            "quantity": item.quantity,
        }
        return JsonResponse({"success": True, "item": item_data})
    except Items.DoesNotExist:
        return JsonResponse({"success": False, "message": "Item not found."})

def purchaseReport(request):
    # Get search query from GET parameters
    itemname = request.GET.get('itemname', '')
    date = request.GET.get('date', '')

    # Start with all items
    items = Items.objects.all()

    # Apply filters based on provided search parameters
    if itemname:
        items = items.filter(itemname__icontains=itemname)  # Adjust 'itemname' if your model has a different field name
    if date:
        items = items.filter(date__icontains=date)  # Adjust 'date' to your model's date field if different

    return render(request, 'purchaseReport.html', {'items': items, 'search_term': itemname, 'search_date': date})

def deleteItem(request,pk):
    try:
        staff = Items.objects.get(id=pk)
        staff.delete()

    except ObjectDoesNotExist:
        pass
    base_url = reverse('viewItem')
    return redirect(base_url)

