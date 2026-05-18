from django.urls import path
from . import views

urlpatterns = [
    # ====================== Home & Products ======================
    path("", views.HomeView.as_view(), name="home"),
    path("products/", views.ProductListView.as_view(), name="product_list"),
    # Updated to use slug for better SEO
    path(
        "product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path("categories/", views.CategoryListView.as_view(), name="categories"),
    path(
        "category/<slug:slug>/",
        views.CategoryDetailView.as_view(),
        name="category_detail",
    ),
    # ====================== Cart ======================
    path("cart/", views.cart_view, name="cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"
    ),
    # ====================== Wishlist ======================
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path(
        "wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"
    ),
    path(
        "wishlist/remove/<int:product_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist",
    ),
    # ====================== Authentication ======================
    path("register/", views.register, name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    # ====================== Checkout & Orders ======================
    path("checkout/", views.checkout, name="checkout"),
    path(
        "order-success/<int:pk>/",
        views.OrderSuccessView.as_view(),
        name="order_success",
    ),
    path("my-account/", views.my_account, name="my_account"),
    path("my-orders/", views.my_orders, name="my_orders"),
]
