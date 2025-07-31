// lib/providers/cart_provider.dart

import 'package:flutter/material.dart';
import 'package:micromart_frontend/models/cart.dart';
import 'package:micromart_frontend/services/api_service.dart';
import 'package:micromart_frontend/providers/auth_provider.dart';

class CartProvider with ChangeNotifier {
  Cart? _cart;
  bool _isLoading = false;
  final ApiService _apiService = ApiService();
  final AuthProvider _authProvider;

  CartProvider(this._authProvider) {
    debugPrint('CartProvider: Initializing. Setting up auth listener.');
    _authProvider.addListener(_onAuthChange);
    _loadCart(); // Initial load
  }

  @override
  void dispose() {
    _authProvider.removeListener(_onAuthChange);
    super.dispose();
  }

  void _onAuthChange() {
    debugPrint('CartProvider: Auth state changed. Reloading cart...');
    _loadCart();
  }

  Cart? get cart => _cart;
  bool get isLoading => _isLoading;

  Future<void> _loadCart() async {
    debugPrint(
      'CartProvider: _loadCart called. Is authenticated: ${_authProvider.isAuthenticated}',
    );
    if (!_authProvider.isAuthenticated) {
      _cart = null;
      debugPrint('CartProvider: User unauthenticated, clearing cart locally.');
      notifyListeners();
      return;
    }

    _isLoading = true;
    notifyListeners();
    try {
      final token = await _authProvider.getValidAccessToken();
      debugPrint(
        'CartProvider: _loadCart - Got token: ${token != null ? "YES" : "NO"}',
      );
      if (token != null) {
        _cart = await _apiService.getCart(token);
        debugPrint('CartProvider: Cart loaded successfully from API.');
      } else {
        _cart = null;
        debugPrint('CartProvider: No valid token, clearing cart locally.');
      }
    } catch (e, stacktrace) {
      debugPrint('CartProvider: Failed to load cart from API: $e');
      debugPrint('Stacktrace: $stacktrace');
      _cart = null;
    } finally {
      _isLoading = false;
      notifyListeners();
      debugPrint('CartProvider: _loadCart finished. Notifying listeners.');
    }
  }

  Future<bool> addToCart(int productId, int quantity) async {
    if (!_authProvider.isAuthenticated) {
      debugPrint('CartProvider: addToCart - Not authenticated.');
      return false;
    }
    _isLoading = true;
    notifyListeners();
    try {
      final token = await _authProvider.getValidAccessToken();
      if (token != null) {
        _cart = await _apiService.addToCart(token, productId, quantity);
        _isLoading = false;
        notifyListeners();
        debugPrint('CartProvider: addToCart - Success.');
        return true;
      }
      _isLoading = false;
      notifyListeners();
      debugPrint('CartProvider: addToCart - No valid token for API call.');
      return false;
    } catch (e, stacktrace) {
      _isLoading = false;
      notifyListeners();
      debugPrint('CartProvider: Failed to add to cart in CartProvider: $e');
      debugPrint('Stacktrace: $stacktrace');
      return false;
    }
  }

  Future<bool> adjustItemQuantity(
    int productId,
    String action,
    int changeBy,
  ) async {
    if (!_authProvider.isAuthenticated) {
      return false;
    }
    _isLoading = true;
    notifyListeners();
    try {
      final token = await _authProvider.getValidAccessToken();
      if (token != null) {
        _cart = await _apiService.adjustCartItemQuantity(
          token,
          productId,
          action,
          changeBy,
        );
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e, stacktrace) {
      _isLoading = false;
      notifyListeners();
      debugPrint('Failed to adjust item quantity: $e');
      debugPrint('Stacktrace: $stacktrace');
      return false;
    }
  }

  Future<bool> removeFromCart(int productId) async {
    if (!_authProvider.isAuthenticated) {
      return false;
    }
    _isLoading = true;
    notifyListeners();
    try {
      final token = await _authProvider.getValidAccessToken();
      if (token != null) {
        _cart = await _apiService.removeFromCart(token, productId);
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e, stacktrace) {
      _isLoading = false;
      notifyListeners();
      debugPrint('Failed to remove from cart: $e');
      debugPrint('Stacktrace: $stacktrace');
      return false;
    }
  }

  Future<bool> clearCart() async {
    if (!_authProvider.isAuthenticated) {
      return false;
    }
    _isLoading = true;
    notifyListeners();
    try {
      final token = await _authProvider.getValidAccessToken();
      if (token != null) {
        await _apiService.clearCart(token);
        _cart = Cart(
          id: _cart!.id,
          user: _cart!.user,
          cartItems: [],
          totalItems: 0,
          totalAmount: 0.0,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e, stacktrace) {
      _isLoading = false;
      notifyListeners();
      debugPrint('Failed to clear cart: $e');
      debugPrint('Stacktrace: $stacktrace');
      return false;
    }
  }

  Future<bool> placeOrder() async {
    if (!_authProvider.isAuthenticated ||
        _cart == null ||
        _cart!.cartItems.isEmpty) {
      return false;
    }
    _isLoading = true;
    notifyListeners();
    try {
      final token = await _authProvider.getValidAccessToken();
      if (token != null) {
        await _apiService.placeOrder(token);
        _cart = Cart(
          id: _cart!.id,
          user: _cart!.user,
          cartItems: [],
          totalItems: 0,
          totalAmount: 0.0,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e, stacktrace) {
      _isLoading = false;
      notifyListeners();
      debugPrint('Failed to place order: $e');
      debugPrint('Stacktrace: $stacktrace');
      return false;
    }
  }
}
