from django.contrib.auth import views as auth_views

from django.urls import path
from common.views import (
    HomeView, LoginView, ForgotPasswordView, LogoutView,
    ChangePasswordView, ProfileView,
    UsersListView, CreateUserView, UpdateUserView, UserDetailView,
    UserDeleteView, PasswordResetView,
    DocumentListView, document_create, document_update,
    DocumentDetailView, DocumentDeleteView,
    download_document, change_user_status, download_attachment,
    add_comment, edit_comment, remove_comment,
    api_settings, add_api_settings, view_api_settings,
    update_api_settings, delete_api_settings,
    change_passsword_by_admin,
    EmpresasListView, EmpresaDetailView, CreateEmpresaView, UpdateEmpresaView,
    EmpresaDeleteView, change_empresa_status,
    ImpuestosListView, ImpuestoDetailView, CreateImpuestoView, UpdateImpuestoView,
    ImpuestoDeleteView, change_empresa_status
)
from django.conf.urls.static import static
from django.conf import settings

app_name = 'common'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/',
         ForgotPasswordView.as_view(), name='forgot_password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-password/',
         ChangePasswordView.as_view(), name='change_password'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # User views
    path('users/list/', UsersListView.as_view(), name='users_list'),
    path('users/create/', CreateUserView.as_view(), name='create_user'),
    path('users/<int:pk>/edit/', UpdateUserView.as_view(), name="edit_user"),
    path('users/<int:pk>/view/', UserDetailView.as_view(), name='view_user'),
    path('users/<int:pk>/delete/',
         UserDeleteView.as_view(), name='remove_user'),

    # Empresas views
    path('empresas/list/', EmpresasListView.as_view(), name='empresas_list'),
    path('empresas/create/', CreateEmpresaView.as_view(), name='create_empresa'),
    path('empresas/<int:pk>/edit/', UpdateEmpresaView.as_view(), name="edit_empresa"),
    path('empresas/<int:pk>/view/', EmpresaDetailView.as_view(), name='view_empresa'),
    path('empresas/<int:pk>/delete/', EmpresaDeleteView.as_view(), name='remove_empresa'),

    # Impuestos views
    path('impuestos/list/', ImpuestosListView.as_view(), name='impuestos_list'),
    path('impuestos/create/', CreateImpuestoView.as_view(), name='create_impuesto'),
    path('impuestos/<int:pk>/edit/', UpdateImpuestoView.as_view(), name="edit_impuesto"),
    path('impuestos/<int:pk>/view/', ImpuestoDetailView.as_view(), name='view_impuesto'),
    path('impuestos/<int:pk>/delete/', ImpuestoDeleteView.as_view(), name='remove_impuesto'),


    path(
        'password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),

    # Document
    path('documents/list/', DocumentListView.as_view(), name='doc_list'),
    path('documents/create/', document_create, name='create_doc'),
    path('documents/<int:pk>/edit/', document_update, name="edit_doc"),
    path('documents/<int:pk>/view/',
         DocumentDetailView.as_view(), name='view_doc'),
    path('documents/<int:pk>/delete/',
         DocumentDeleteView.as_view(), name='remove_doc'),

    # download
    path('documents/<int:pk>/download/',
         download_document, name='download_document'),

    # download_attachment
    path('attachments/<int:pk>/download/',
         download_attachment, name='download_attachment'),

    path('user/status/<int:pk>/',
         change_user_status, name='change_user_status'),
    path('empresa/status/<int:pk>/',
         change_empresa_status, name='change_empresa_status'),

    path('comment/add/', add_comment, name="add_comment"),
    path('comment/<int:pk>/edit/', edit_comment, name="edit_comment"),
    path('comment/remove/', remove_comment, name="remove_comment"),

    # settings
    path('api/settings/', api_settings, name="api_settings"),
    path('api/settings/add/', add_api_settings, name="add_api_settings"),
    path('api/settings/<int:pk>/',
         view_api_settings, name="view_api_settings"),
    path('api/settings/<int:pk>/update/',
         update_api_settings, name="update_api_settings"),
    path('api/settings/<int:pk>/delete/',
         delete_api_settings, name="delete_api_settings"),

    path('change-password-by-admin/', change_passsword_by_admin,
         name="change_passsword_by_admin"),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
