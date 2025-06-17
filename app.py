from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Cliente, Producto, Venta, DetalleVenta, Credito, Pago, ObservacionPago
from utils_pdf import generar_pdf_venta
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-local')

db.init_app(app)


with app.app_context():
    db.create_all()
    if Producto.query.count() == 0:
        productos_predefinidos = [
            {
                "nombre": "Librero Pequeño",
                "precio_unitario": 120,
                "descripcion": "Librero compacto ideal para espacios reducidos.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Librero de Cómputo",
                "precio_unitario": 180,
                "descripcion": "Librero con espacio para equipos de cómputo y libros.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Librero Grande",
                "precio_unitario": 250,
                "descripcion": "Librero amplio con múltiples niveles.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Mesa de Sala",
                "precio_unitario": 200,
                "descripcion": "Mesa central para sala de estar.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Mesa de Cómputo",
                "precio_unitario": 160,
                "descripcion": "Mesa ergonómica para uso con computadora.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Mesa para TV",
                "precio_unitario": 180,
                "descripcion": "Mesa baja para colocar televisor y equipos multimedia.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Cómoda Pequeña",
                "precio_unitario": 140,
                "descripcion": "Cómoda de tamaño reducido con cajones.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Cómoda Grande",
                "precio_unitario": 220,
                "descripcion": "Cómoda espaciosa con múltiples compartimientos.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Cómoda con Espejo",
                "precio_unitario": 260,
                "descripcion": "Cómoda con espejo ideal para dormitorio.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Ropero Junior",
                "precio_unitario": 280,
                "descripcion": "Ropero compacto para habitación infantil.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Ropero Grande",
                "precio_unitario": 350,
                "descripcion": "Ropero grande con divisiones internas.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Ropero con Espejo",
                "precio_unitario": 390,
                "descripcion": "Ropero grande con espejo incorporado.",
                "categoria": "Dormitorio"
            },
            {
                "nombre": "Repostero Metálico Pequeño",
                "precio_unitario": 170,
                "descripcion": "Repostero metálico pequeño para cocina.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Repostero Metálico Grande",
                "precio_unitario": 250,
                "descripcion": "Repostero metálico grande y resistente.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Repostero Melamine Pequeño",
                "precio_unitario": 200,
                "descripcion": "Repostero melamine pequeño con estantes.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Repostero Melamine Grande",
                "precio_unitario": 280,
                "descripcion": "Repostero grande de melamine.",
                "categoria": "Cocina"
            },
            {
                "nombre": "Colchón Sueños plaza y media",
                "precio_unitario": 320,
                "descripcion": "Colchón marca Sueños para plaza y media.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Dormitel plaza y media",
                "precio_unitario": 300,
                "descripcion": "Colchón Dormitel cómodo y económico.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Sueños 2 plazas",
                "precio_unitario": 420,
                "descripcion": "Colchón Sueños de 2 plazas de alta durabilidad.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Dormitel 2 plazas",
                "precio_unitario": 390,
                "descripcion": "Colchón Dormitel tamaño 2 plazas.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Colchón Paraíso",
                "precio_unitario": 500,
                "descripcion": "Colchón Paraíso ortopédico.",
                "categoria": "Colchones"
            },
            {
                "nombre": "Zapatero",
                "precio_unitario": 120,
                "descripcion": "Zapatero práctico para organizar calzado.",
                "categoria": "Accesorios"
            },
            {
                "nombre": "Zapatero con Espejo",
                "precio_unitario": 180,
                "descripcion": "Zapatero vertical con espejo frontal.",
                "categoria": "Accesorios"
            },
            {
                "nombre": "Estante Multiuso",
                "precio_unitario": 130,
                "descripcion": "Estante para múltiples usos domésticos.",
                "categoria": "Muebles"
            },
            {
                "nombre": "Perchero",
                "precio_unitario": 90,
                "descripcion": "Perchero de pie para ropa y accesorios.",
                "categoria": "Accesorios"
            }
        ]

        for producto in productos_predefinidos:
            db.session.add(Producto(
                nombre=producto["nombre"],
                descripcion=producto["descripcion"],
                precio_unitario=producto["precio_unitario"],
                stock=20,
                categoria=producto["categoria"]
            ))

        db.session.commit()


@app.route('/')
def index():
    print(Cliente.__table__.columns.keys())
    pro = Producto.query.all()
    print(pro[0].nombre, pro[0].stock)
    return render_template('index.html')

@app.route('/ver-clientes')
def clientes():
    lista = Cliente.query.all()
    return render_template('ver_clientes.html', clientes=lista)

@app.route('/registrar-cliente', methods=['POST', 'GET'])
def registrar_cliente():
    if request.method == 'POST':
        dni = request.form['dni']

        # Verificar si ya existe un cliente con ese DNI
        cliente_existente = Cliente.query.filter_by(dni=dni).first()
        if cliente_existente:
            flash('El DNI ya está registrado. Por favor, ingrese uno diferente.', 'danger')
            return redirect(url_for('registrar_cliente'))

        # Si no existe, crear nuevo cliente
        nuevo_cliente = Cliente(
            nombre=request.form['nombre'],
            apellido_paterno=request.form['apellido_paterno'],
            apellido_materno=request.form['apellido_materno'],
            dni=dni,
            direccion=request.form.get('direccion'),
            referencia_direccion=request.form.get('referencia_direccion'),
            telefono_principal=request.form['telefono_principal'],
            telefono_alternativo=request.form.get('telefono_alternativo'),
            email=request.form.get('email')
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        flash('Cliente registrado con éxito.', 'success')
        return redirect(url_for('registrar_cliente'))

    return render_template('registrar_cliente.html')

@app.route('/productos', methods=['GET', 'POST'])
def productos():
    if request.method == 'POST':
        nuevo = Producto(
            nombre=request.form['nombre'],
            descripcion=request.form.get('descripcion'),
            precio_unitario=request.form['precio_unitario'],
            stock=request.form['stock'],
            categoria=request.form.get('categoria')
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Producto agregado con éxito.', 'success')
        return redirect(url_for('productos'))

    lista = Producto.query.all()
    return render_template('productos.html', productos=lista)

@app.route('/productos/editar/<int:producto_id>', methods=['POST'])
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    producto.nombre = request.form['nombre']
    producto.descripcion = request.form.get('descripcion')
    producto.precio_unitario = request.form['precio_unitario']
    producto.stock = request.form['stock']
    producto.categoria = request.form.get('categoria')
    db.session.commit()
    flash('Producto actualizado con éxito.', 'success')
    return redirect(url_for('productos'))

@app.route('/productos/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'warning')
    return redirect(url_for('productos'))

@app.route('/ventas', methods=['GET', 'POST'])
def ventas():
    clientes = Cliente.query.all()
    productos = Producto.query.all()

    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        tipo_pago = request.form['tipo_pago']
        fecha_venta = datetime.now()  # Fecha y hora actual del servidor
        detalles = []

        total = 0
        for i in range(len(request.form.getlist('producto_id'))):
            producto_id = int(request.form.getlist('producto_id')[i])
            cantidad = int(request.form.getlist('cantidad')[i])
            producto = Producto.query.get(producto_id)
            precio = float(producto.precio_unitario)
            subtotal = cantidad * precio
            total += subtotal
            detalles.append({
                'producto': producto,
                'cantidad': cantidad,
                'precio': precio
            })

        venta = Venta(
            cliente_id=cliente_id,
            fecha_venta=fecha_venta,
            tipo_pago=tipo_pago,
            total=total
        )
        db.session.add(venta)
        db.session.flush()  # Para obtener venta_id sin hacer commit aún

        for item in detalles:
            detalle = DetalleVenta(
                venta_id=venta.venta_id,
                producto_id=item['producto'].producto_id,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            db.session.add(detalle)

            producto = item['producto']
            if producto.stock < item['cantidad']:
                db.session.rollback()
                return f"No hay suficiente stock para {producto.nombre}", 400

            producto.stock -= item['cantidad']
        # Si es crédito, crear el crédito
        if tipo_pago.lower() == 'crédito':
            credito = Credito(
                venta_id=venta.venta_id,
                saldo_inicial=total,
                saldo_actual=total,
                estado='Pendiente',
                frecuencia_pago=request.form['frecuencia_pago'],
                fecha_proxima_pago=datetime.strptime(request.form['fecha_proxima_pago'], '%Y-%m-%d')
            )
            db.session.add(credito)

        db.session.commit()

        cliente = Cliente.query.get(cliente_id)
        venta = Venta.query.get(venta.venta_id)
        detalles_db = DetalleVenta.query.filter_by(venta_id=venta.venta_id).all()

        return generar_pdf_venta(cliente, venta, detalles_db)

    ventas_historial = Venta.query.order_by(Venta.fecha_venta.desc()).all()
    return render_template('ventas.html', clientes=clientes, productos=productos, ventas=ventas_historial)


@app.route('/detalle_venta/<int:venta_id>')
def detalle_venta(venta_id):
    venta = Venta.query.get_or_404(venta_id)

    detalle = {
        "exito": True,
        "cliente": f"{venta.cliente.nombre} {venta.cliente.apellido_paterno}",
        "fecha": venta.fecha_venta.strftime('%d/%m/%Y %H:%M:%S'),
        "tipo_pago": venta.tipo_pago,
        "total": float(venta.total),
        "productos": []
    }

    for item in venta.detalles:
        detalle["productos"].append({
            "nombre": item.producto.nombre,
            "cantidad": item.cantidad,
            "precio_unitario": float(item.precio_unitario)
        })

    return jsonify(detalle)




# Ver créditos activos
@app.route('/creditos')
def ver_creditos():
    creditos = Credito.query.filter(Credito.estado != 'Pagado').all()
    return render_template('creditos.html', creditos=creditos)

# Obtener detalle de crédito
@app.route('/detalle_credito/<int:credito_id>')
def detalle_credito(credito_id):
    credito = Credito.query.get_or_404(credito_id)
    cliente = credito.venta.cliente
    detalles = DetalleVenta.query.filter_by(venta_id=credito.venta_id).all()
    pagos = Pago.query.filter_by(credito_id=credito_id).order_by(Pago.fecha_pago.asc()).all()

    productos = [{
        "nombre": d.producto.nombre,
        "cantidad": d.cantidad,
        "precio_unitario": float(d.precio_unitario)
    } for d in detalles]

    lista_pagos = []
    for p in pagos:
        observaciones = [{
            "texto": o.texto,
            "fecha": o.fecha.strftime('%H:%M') #%d-%m-%Y %H:%M
        } for o in p.observaciones]
        lista_pagos.append({
            "fecha": p.fecha_pago.strftime('%d-%m-%Y'),
            "monto": float(p.monto),
            "observaciones": observaciones
        })

    return jsonify({
        "exito": True,
        "cliente": f"{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}",
        "direccion": cliente.direccion,
        "telefono": cliente.telefono_principal,
        "productos": productos,
        "pagos": lista_pagos,
        "saldo_actual": float(credito.saldo_actual)
    })

# Agregar pago con observaciones
@app.route('/agregar_pago/<int:credito_id>', methods=['POST'])
def agregar_pago(credito_id):
    credito = Credito.query.get_or_404(credito_id)

    try:
        data = request.json
        monto = float(data['monto'])
        textos_obs = data.get('observaciones', [])  # Lista de textos
    except (ValueError, KeyError):
        return jsonify({"exito": False, "mensaje": "Datos inválidos"})

    nuevo_saldo = float(credito.saldo_actual) - monto
    nuevo_saldo = max(nuevo_saldo, 0)

    nuevo_pago = Pago(
        credito_id=credito_id,
        fecha_pago=datetime.now(),
        monto=monto
    )
    db.session.add(nuevo_pago)
    db.session.flush()  # Para obtener pago_id antes del commit

    for texto in textos_obs:
        obs = ObservacionPago(
            pago_id=nuevo_pago.pago_id,
            texto=texto,
            fecha=datetime.now()
        )
        db.session.add(obs)

    credito.saldo_actual = nuevo_saldo
    if nuevo_saldo == 0:
        credito.estado = 'Pagado'

    db.session.commit()

    return jsonify({
        "exito": True,
        "saldo_actual": nuevo_saldo
    })
    
