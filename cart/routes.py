from flask import (
    render_template, redirect, url_for, flash, request, jsonify,
    send_file, abort, current_app
)
from flask_login import login_required, current_user
from cart import bp
from app1 import db
from models import Product, CartItem, Order, OrderItem, Invoice
from forms import CartItemForm
import os
from datetime import datetime
from fpdf import FPDF


@bp.route('/')
@login_required
def index():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.total_price for item in cart_items)
    return render_template('cart/index.html', cart_items=cart_items, total=total)

@bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(request.referrer or url_for('products.index'))

@bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = request.form.get('quantity', 1, type=int)
    
    if quantity > 0:
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated!', 'success')
    else:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'info')
    
    return redirect(url_for('cart.index'))

@bp.route('/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart!', 'info')
    return redirect(url_for('cart.index'))

@bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty!', 'warning')
        return redirect(url_for('cart.index'))
    
    # Calculate total
    total = sum(item.total_price for item in cart_items)
    
    # Create order
    order = Order(user_id=current_user.id, total_amount=total)
    db.session.add(order)
    db.session.flush()  # Get the order ID
    
    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)
    
    # Clear cart
    for cart_item in cart_items:
        db.session.delete(cart_item)
    
    # --- INICIO: GENERAR FACTURA PDF CON FPDF2 ---
    try:
        # Usar ruta absoluta
        pdf_dir = os.path.join(current_app.root_path, 'static', 'invoices')
        os.makedirs(pdf_dir, exist_ok=True)

        # Generar número de factura
        invoice_number = f"INV-{order.id}-{datetime.now().strftime('%Y%m%d')}"

        # Crear registro en base de datos
        invoice = Invoice(invoice_number=invoice_number, order_id=order.id)
        db.session.add(invoice)
        db.session.flush()

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # --- ESTILO PROFESIONAL PARA PANADERÍA ---
        # Logo (placeholder - puedes reemplazarlo con tu logo real)
        # if os.path.exists(os.path.join(current_app.root_path, 'static', 'images', 'logo_panaderia.png')):
        #     pdf.image(os.path.join(current_app.root_path, 'static', 'images', 'logo_panaderia.png'), x=10, y=10, w=40)

        # Título principal
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(210, 105, 30)  # Color chocolate
        pdf.cell(0, 15, "Panadería Delicias", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)  # Volver a negro
        pdf.ln(5)

        # Subtítulo
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, "Calidad y Sabor en Cada Bocado", ln=True, align='C')
        pdf.ln(10)

        # Número de factura
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(255, 248, 220)  # Fondo beige claro
        pdf.cell(0, 12, f"FACTURA N° {invoice_number}", ln=True, align='C', fill=True)
        pdf.ln(15)

        # Información del cliente y fecha
        pdf.set_font("Arial", size=11)
        client_name = order.user.username if order.user else "Cliente Desconocido"
        pdf.cell(0, 10, f"Cliente: {client_name}", ln=True)
        
        date_str = order.created_at.strftime('%d/%m/%Y') if order.created_at else "Fecha no disponible"
        pdf.cell(0, 10, f"Fecha: {date_str}", ln=True)
        pdf.ln(15)

        # Tabla de productos
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(245, 222, 179)  # Fondo beige dorado
        pdf.set_text_color(139, 69, 19)   # Color marrón oscuro
        pdf.cell(90, 12, "Producto", border=1, fill=True)
        pdf.cell(30, 12, "Cantidad", border=1, fill=True, align='C')
        pdf.cell(35, 12, "Precio", border=1, fill=True, align='R')
        pdf.cell(35, 12, "Total", border=1, fill=True, align='R')
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

        pdf.set_font("Arial", size=10)
        for item in order.order_items:
            product_name = item.product.name if item.product else "Producto eliminado"
            # Limitar longitud del nombre
            if len(product_name) > 25:
                product_name = product_name[:22] + "..."
                
            pdf.cell(90, 10, product_name, border=1)
            pdf.cell(30, 10, str(item.quantity), border=1, align='C')
            pdf.cell(35, 10, f"${item.price:.2f}", border=1, align='R')
            pdf.cell(35, 10, f"${item.total_price:.2f}", border=1, align='R')
            pdf.ln()

        # Total final
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(155, 12, "TOTAL", border=1, fill=True, align='R')
        pdf.set_text_color(255, 0, 0)  # Rojo para el total
        pdf.cell(35, 12, f"${order.total_amount:.2f}", border=1, fill=True, align='R')
        pdf.set_text_color(0, 0, 0)

        # Mensaje de agradecimiento
        pdf.ln(20)
        pdf.set_font("Arial", 'I', 11)
        pdf.set_text_color(210, 105, 30)
        pdf.cell(0, 10, "¡Gracias por su compra! Vuelva pronto.", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Para reclamos o consultas: contacto@panaderiadelicias.com", ln=True, align='C')

        # Guardar PDF
        pdf_filename = f"invoice_{invoice.id}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)
        pdf.output(pdf_path)

        # Guardar ruta en DB
        invoice.pdf_file_path = os.path.join('static', 'invoices', pdf_filename)
        db.session.commit()

        flash('¡Factura generada con éxito!', 'success')

    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        flash('Orden creada, pero no se pudo generar la factura.', 'warning')
    # --- FIN: GENERAR FACTURA PDF CON FPDF2 ---
    
    db.session.commit()
    flash('Order placed successfully!', 'success')
    
     return redirect(url_for('cart.order_confirmation', order_id=order.id))

@bp.route('/confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    return render_template('orders/confirmation.html', order=order)

@bp.route('/download_invoice/<int:order_id>')
@login_required
def download_invoice(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if not order.invoice or not order.invoice.pdf_file_path:
        abort(404, description="Factura no encontrada.")
    
    # Usar current_app.root_path
    pdf_path = os.path.join(current_app.root_path, order.invoice.pdf_file_path)
    
    if not os.path.exists(pdf_path):
        abort(404, description="Archivo PDF no encontrado.")
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"factura_{order.id}.pdf",
        mimetype='application/pdf'
    )
