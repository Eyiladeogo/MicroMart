// lib/providers/auth_provider.dart

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:jwt_decoder/jwt_decoder.dart';
import 'package:micromart_frontend/services/api_service.dart';

class AuthProvider with ChangeNotifier {
  String? _accessToken;
  String? _refreshToken;
  Map<String, dynamic>? _userPayload;
  bool _isLoading = false;

  final ApiService _apiService = ApiService();

  bool get isAuthenticated =>
      _accessToken != null && !JwtDecoder.isExpired(_accessToken!);
  String? get accessToken => _accessToken;
  String? get refreshToken => _refreshToken;
  Map<String, dynamic>? get userPayload => _userPayload;
  bool get isLoading => _isLoading;

  AuthProvider() {
    debugPrint('AuthProvider: Initializing and loading tokens...');
    _loadTokens();
  }

  Future<void> _loadTokens() async {
    _isLoading = true;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    _accessToken = prefs.getString('accessToken');
    _refreshToken = prefs.getString('refreshToken');

    debugPrint(
      'AuthProvider: Loaded tokens. Access: $_accessToken, Refresh: $_refreshToken',
    );

    if (_accessToken != null && !JwtDecoder.isExpired(_accessToken!)) {
      _userPayload = JwtDecoder.decode(_accessToken!);
      debugPrint('AuthProvider: Access token valid. User authenticated.');
    } else if (_refreshToken != null && !JwtDecoder.isExpired(_refreshToken!)) {
      debugPrint('AuthProvider: Access token expired, attempting refresh...');
      await _refreshAccessToken();
    } else {
      _accessToken = null;
      _refreshToken = null;
      _userPayload = null;
      debugPrint('AuthProvider: No valid tokens. User unauthenticated.');
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> _saveTokens(String access, String refresh) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('accessToken', access);
    await prefs.setString('refreshToken', refresh);
    _accessToken = access;
    _refreshToken = refresh;
    _userPayload = JwtDecoder.decode(access);
    debugPrint(
      'AuthProvider: Tokens saved and user payload decoded. Notifying listeners.',
    );
    notifyListeners(); // This is the key call that CartProvider listens to
  }

  Future<void> _clearTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('accessToken');
    await prefs.remove('refreshToken');
    _accessToken = null;
    _refreshToken = null;
    _userPayload = null;
    debugPrint('AuthProvider: Tokens cleared. Notifying listeners.');
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      debugPrint('AuthProvider: Attempting login for $email...');
      final response = await _apiService.loginUser(email, password);
      await _saveTokens(response['access'], response['refresh']);
      _isLoading = false;
      debugPrint('AuthProvider: Login successful.');
      return true;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      debugPrint('AuthProvider: Login failed: $e');
      return false;
    }
  }

  Future<bool> register(String username, String email, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      debugPrint(
        'AuthProvider: Attempting registration for $username ($email)...',
      );
      await _apiService.registerUser(username, email, password);
      _isLoading = false;
      debugPrint(
        'AuthProvider: Registration successful. Attempting auto-login.',
      );
      return await login(email, password);
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      debugPrint('AuthProvider: Registration failed: $e');
      return false;
    }
  }

  Future<void> logout() async {
    debugPrint('AuthProvider: Logging out...');
    await _clearTokens();
  }

  Future<bool> _refreshAccessToken() async {
    if (_refreshToken == null || JwtDecoder.isExpired(_refreshToken!)) {
      debugPrint(
        'AuthProvider: No refresh token or refresh token expired. Clearing all tokens.',
      );
      await _clearTokens();
      return false;
    }
    try {
      debugPrint('AuthProvider: Refreshing access token...');
      final response = await _apiService.refreshToken(_refreshToken!);
      await _saveTokens(response['access'], _refreshToken!);
      debugPrint('AuthProvider: Access token refreshed successfully.');
      return true;
    } catch (e) {
      debugPrint('AuthProvider: Token refresh failed: $e');
      await _clearTokens();
      return false;
    }
  }

  Future<String?> getValidAccessToken() async {
    if (_accessToken == null) {
      debugPrint(
        'AuthProvider: getValidAccessToken - No access token available.',
      );
      return null;
    }
    if (JwtDecoder.isExpired(_accessToken!)) {
      debugPrint(
        'AuthProvider: getValidAccessToken - Access token expired, attempting refresh.',
      );
      bool refreshed = await _refreshAccessToken();
      if (!refreshed) {
        debugPrint(
          'AuthProvider: getValidAccessToken - Could not refresh token.',
        );
        return null;
      }
    }
    debugPrint(
      'AuthProvider: getValidAccessToken - Returning valid access token.',
    );
    return _accessToken;
  }
}
