from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from models import User, Category

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(message="El correo es obligatorio"), Email(message="Correo inválido")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es obligatoria")])

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(message="El nombre de usuario es obligatorio"), Length(min=4, max=20, message="Debe tener entre 4 y 20 caracteres")])
    email = StringField('Correo electrónico', validators=[DataRequired(message="El correo es obligatorio"), Email(message="Correo inválido")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="La contraseña es obligatoria"), Length(min=6, message="Debe tener al menos 6 caracteres")])
    password2 = PasswordField('Repite la contraseña', validators=[DataRequired(message="Debes repetir la contraseña"), EqualTo('password', message="Las contraseñas no coinciden")])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('El nombre de usuario ya existe. Por favor elige otro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('El correo ya está registrado. Usa uno diferente.')

class ProductForm(FlaskForm):
    name = StringField('Nombre del producto', validators=[DataRequired(message="El nombre es obligatorio"), Length(max=100, message="Máximo 100 caracteres")])
    description = TextAreaField('Descripción')
    price = DecimalField('Precio', validators=[DataRequired(message="El precio es obligatorio"), NumberRange(min=0.01, message="El precio debe ser mayor a 0")])
    image_url = StringField('URL de la imagen', validators=[Length(max=200, message="Máximo 200 caracteres")])
    category_id = SelectField('Categoría', coerce=int, validators=[DataRequired(message="La categoría es obligatoria")])
    featured = BooleanField('Producto destacado')
    active = BooleanField('Activo', default=True)
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class CategoryForm(FlaskForm):
    name = StringField('Nombre de la categoría', validators=[DataRequired(message="El nombre es obligatorio"), Length(max=80, message="Máximo 80 caracteres")])
    description = TextAreaField('Descripción (opcional)')

class CartItemForm(FlaskForm):
    quantity = IntegerField('Cantidad', validators=[DataRequired(message="La cantidad es obligatoria"), NumberRange(min=1, message="Debe ser al menos 1")])
