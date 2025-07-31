// lib/services/api_service.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:micromart_frontend/utils/constants.dart';
import 'package:micromart_frontend/models/product.dart';
import 'package:micromart_frontend/models/cart.dart';

class ApiService {
  final String baseUrl;

  ApiService({String? baseUrl}) : baseUrl = baseUrl ?? kBaseUrl;

  Future<Map<String, dynamic>> _sendAuthenticatedRequest(
    String endpoint,
    String method,
    String? token, {
    Map<String, dynamic>? body,
  }) async {
    final url = Uri.parse('$baseUrl$endpoint');
    final headers = <String, String>{'Content-Type': 'application/json'};
    if (token != null) {
      headers['Authorization'] = 'Bearer $token';
    }

    http.Response response;
    switch (method.toUpperCase()) {
      case 'GET':
        response = await http.get(url, headers: headers);
        break;
      case 'POST':
        response = await http.post(
          url,
          headers: headers,
          body: json.encode(body),
        );
        break;
      case 'PATCH':
        response = await http.patch(
          url,
          headers: headers,
          body: json.encode(body),
        );
        break;
      case 'PUT':
        response = await http.put(
          url,
          headers: headers,
          body: json.encode(body),
        );
        break;
      case 'DELETE':
        response = await http.delete(
          url,
          headers: headers,
          body: json.encode(body),
        );
        break;
      default:
        throw Exception('Unsupported HTTP method: $method');
    }

    // --- FIX START ---
    if (response.statusCode >= 200 && response.statusCode < 300) {
      // If the response is 204 No Content, or the body is empty, return an empty map.
      // This prevents json.decode from throwing FormatException.
      if (response.statusCode == 204 || response.body.isEmpty) {
        return {};
      }
      try {
        return json.decode(response.body);
      } catch (e) {
        // This catch block will specifically catch FormatException if body is not valid JSON
        throw Exception(
          'Failed to parse JSON response from $endpoint: ${response.body}',
        );
      }
    } else {
      // --- FIX END ---
      String errorMessage = 'An error occurred';
      try {
        final errorData = json.decode(response.body);
        if (errorData is Map && errorData.containsKey('detail')) {
          errorMessage = errorData['detail'];
        } else if (errorData is Map && errorData.values.isNotEmpty) {
          errorMessage = errorData.values.first.toString();
        } else {
          errorMessage = response.body;
        }
      } catch (e) {
        errorMessage = response.body;
      }
      throw Exception(
        'Failed to $method $endpoint: ${response.statusCode} - $errorMessage',
      );
    }
  }

  // --- Authentication ---
  Future<Map<String, dynamic>> registerUser(
    String username,
    String email,
    String password,
  ) async {
    return await _sendAuthenticatedRequest(
      kRegisterEndpoint,
      'POST',
      null,
      body: {
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password,
      },
    );
  }

  Future<Map<String, dynamic>> loginUser(String email, String password) async {
    return await _sendAuthenticatedRequest(
      kTokenObtainPairEndpoint,
      'POST',
      null,
      body: {'email': email, 'password': password},
    );
  }

  Future<Map<String, dynamic>> refreshToken(String refreshToken) async {
    return await _sendAuthenticatedRequest(
      kTokenRefreshEndpoint,
      'POST',
      null,
      body: {'refresh': refreshToken},
    );
  }

  // --- Products ---
  Future<Map<String, dynamic>> getProducts({
    String? search,
    String? ordering,
    double? minPrice,
    double? maxPrice,
    int? page,
    int? pageSize,
    String? token,
  }) async {
    final queryParams = <String, String>{};
    if (search != null && search.isNotEmpty) queryParams['search'] = search;
    if (ordering != null && ordering.isNotEmpty)
      queryParams['ordering'] = ordering;
    if (minPrice != null) queryParams['price_min'] = minPrice.toString();
    if (maxPrice != null) queryParams['price_max'] = maxPrice.toString();
    if (page != null) queryParams['page'] = page.toString();
    if (pageSize != null) queryParams['page_size'] = pageSize.toString();

    String queryString = Uri(queryParameters: queryParams).query;
    final endpoint =
        '$kProductsEndpoint${queryString.isEmpty ? '' : '?$queryString'}';

    final responseData = await _sendAuthenticatedRequest(
      endpoint,
      'GET',
      token,
    );

    final List<dynamic> results = responseData['results'];
    final List<Product> products = results
        .map((json) => Product.fromJson(json))
        .toList();

    final int count = responseData['count'];

    return {'products': products, 'count': count};
  }

  // --- Cart ---
  Future<Cart> getCart(String token) async {
    final responseData = await _sendAuthenticatedRequest(
      kCartEndpoint,
      'GET',
      token,
    );
    return Cart.fromJson(responseData);
  }

  Future<Cart> addToCart(String token, int productId, int quantity) async {
    final responseData = await _sendAuthenticatedRequest(
      kAddToCartEndpoint,
      'POST',
      token,
      body: {'product_id': productId, 'quantity': quantity},
    );
    return Cart.fromJson(responseData);
  }

  Future<Cart> adjustCartItemQuantity(
    String token,
    int productId,
    String action,
    int changeBy,
  ) async {
    final responseData = await _sendAuthenticatedRequest(
      kAdjustCartQuantityEndpoint,
      'PATCH',
      token,
      body: {'product_id': productId, 'action': action, 'change_by': changeBy},
    );
    return Cart.fromJson(responseData['cart']);
  }

  Future<Cart> removeFromCart(String token, int productId) async {
    final responseData = await _sendAuthenticatedRequest(
      kRemoveFromCartEndpoint,
      'PUT', // Ensure this matches your urls.py
      token,
      body: {'product_id': productId},
    );
    return Cart.fromJson(responseData['cart']);
  }

  Future<void> clearCart(String token) async {
    // Note: clearCart in backend now returns 200 OK with cart data.
    // If it were 204 No Content, you'd just await the request.
    final responseData = await _sendAuthenticatedRequest(
      kClearCartEndpoint,
      'DELETE',
      token,
    );
    // If backend returns data, you might want to update the cart in provider
    // For now, it's handled by the provider resetting the cart locally.
  }

  // --- Orders ---
  Future<Map<String, dynamic>> placeOrder(String token) async {
    return await _sendAuthenticatedRequest(kOrdersEndpoint, 'POST', token);
  }

  Future<List<dynamic>> getOrders(
    String token, {
    int? page,
    int? pageSize,
  }) async {
    final queryParams = <String, String>{};
    if (page != null) queryParams['page'] = page.toString();
    if (pageSize != null) queryParams['page_size'] = pageSize.toString();

    String queryString = Uri(queryParameters: queryParams).query;
    final endpoint =
        '$kOrdersEndpoint${queryString.isEmpty ? '' : '?$queryString'}';

    final responseData = await _sendAuthenticatedRequest(
      endpoint,
      'GET',
      token,
    );
    return responseData['results'];
  }
}
