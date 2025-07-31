import 'package:flutter_dotenv/flutter_dotenv.dart';

// Replace with the actual IP address or domain of your Django backend
// If running on a physical device, use your machine's IP address (e.g., '192.168.1.X')
// If running on an emulator/simulator, '10.0.2.2' is the special alias for your host machine
// const String kBaseUrl = 'http://10.0.2.2:8000/api'; // For Android Emulator
// const String kBaseUrl =
//     'http://localhost:8000/api/v1'; // For iOS Simulator or Web
final String kBaseUrl =
    dotenv.env['FLUTTER_BASE_URL'] ?? 'http://localhost:8000/api/v1';

// API Endpoints
const String kRegisterEndpoint = '/auth/register/';
const String kTokenObtainPairEndpoint = '/auth/login/';
const String kTokenRefreshEndpoint = '/auth/token/refresh/';
const String kProductsEndpoint = '/store/products/';
const String kCartEndpoint = '/store/cart/';
const String kAddToCartEndpoint = '/store/cart/';
const String kAdjustCartQuantityEndpoint = '/store/cart/';
const String kRemoveFromCartEndpoint = '/store/cart/';
const String kClearCartEndpoint = '/store/cart/';
const String kOrdersEndpoint = '/store/orders/';
