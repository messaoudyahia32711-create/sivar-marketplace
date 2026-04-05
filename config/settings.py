import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # ⚠️ يجب أن يكون jazzmin في الأعلى
    'jazzmin',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # مكتبات خارجية
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',

    # تطبيقات المشروع (التي بنيناها)
    'apps.users',
    'apps.products',
    'apps.services',
    'apps.cart',
    'apps.orders',
    'apps.reviews',
    'apps.localization',
    'apps.vendors',
    'apps.chat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------------------------------------------------------------
# Database Configuration
# ---------------------------------------------------------------
DB_ENGINE = os.getenv('DB_ENGINE', 'sqlite3')

if DB_ENGINE == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': f'django.db.backends.{DB_ENGINE}',
            'NAME': os.getenv('DB_NAME', 'algerian_marketplace'),
            'USER': os.getenv('DB_USER', 'root'),
            'PASSWORD': os.getenv('DB_PASSWORD', ''),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    # {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    # {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar-dz'
TIME_ZONE = 'Africa/Algiers'
USE_I18N = True
USE_TZ = False

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# ---------------------------------------------------------------
# Django REST Framework Configuration
# ---------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Authentication defaults
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# ---------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'users.log',
        },
    },
    'loggers': {
        'apps.users.views': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# ---------------------------------------------------------------
# JAZZMIN SETTINGS
# ---------------------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "لوحة تحكم المتجر الجزائري",
    "site_header": "إدارة المتجر",
    "site_brand": "Algerian Market",
    "welcome_sign": "مرحباً بك في لوحة التحكم",
    "copyright": "Algerian Market © 2025",
    "search_model": ["users.User", "products.Product", "services.Service", "localization.Wilaya"],
    "topmenu_links": [
        {"name": "🏠 الرئيسية", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "products"},
        {"name": "📘 التوثيق", "url": "https://docs.algerianmarket.com", "new_window": True},
    ],
    "icons": {
        "auth": "fas fa-shield-alt",
        "auth.Group": "fas fa-layer-group",
        "users": "fas fa-users-cog",
        "users.User": "fas fa-user-tie",
        "products": "fas fa-store",
        "products.Product": "fas fa-box-open",
        "products.Category": "fas fa-tags",
        "products.Brand": "fas fa-award",
        "products.Review": "fas fa-star-half-alt",
        "services": "fas fa-hands-helping",
        "services.Service": "fas fa-concierge-bell",
        "services.ServiceCategory": "fas fa-th-large",
        "cart": "fas fa-shopping-bag",
        "cart.Cart": "fas fa-shopping-cart",
        "cart.CartItem": "fas fa-cart-plus",
        "cart.Order": "fas fa-file-invoice-dollar",
        "cart.OrderItem": "fas fa-receipt",
        "localization": "fas fa-globe-africa",
        "localization.Wilaya": "fas fa-map-marked-alt",
        "localization.Commune": "fas fa-map-pin",
        "localization.Daira": "fas fa-map",
    },
    "default_icon_parents": "fas fa-folder-open",
    "default_icon_children": "fas fa-arrow-circle-right",
    "order_with_respect_to": ["users", "products", "services", "cart", "localization", "auth"],
    "hide_apps": [],
    "hide_models": ["auth.User"],
    "custom_links": {
        "products": [
            {"name": "🌐 زيارة المتجر", "url": "/", "icon": "fas fa-external-link-alt", "new_window": True, "permissions": ["products.view_product"]},
        ],
        "users": [
            {"name": "📋 سجل النشاطات", "url": "admin:admin_logentry_changelist", "icon": "fas fa-history", "permissions": ["admin.view_logentry"]},
        ],
    },
    "navigation_expanded": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "users.User": "vertical_tabs",
        "products.Product": "horizontal_tabs",
        "cart.Order": "horizontal_tabs",
    },
    "related_modal_active": True,
    "show_ui_builder": DEBUG,
    "custom_css": "css/admin_custom.css",
    "custom_js": None,
    "show_sidebar": True,
    "use_google_fonts_cdn": True,
    "user_avatar": None,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "materia",
    "dark_mode_theme": "cyborg",
    "navbar": "navbar-white navbar-light",
    "navbar_fixed": True,
    "sidebar": "sidebar-dark-navy",
    "sidebar_fixed": True,
    "sidebar_collapse": True,
    "sidebar_nav_small_text": False,
    "sidebar_nav_flat_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_child_indent": True,
    "body_small_text": False,
    "footer_fixed": False,
    "actions_sticky_top": True,
}
