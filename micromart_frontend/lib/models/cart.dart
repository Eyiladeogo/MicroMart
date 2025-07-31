// lib/models/cart.dart

import 'package:micromart_frontend/models/product.dart';

class CartItem {
  final int id;
  final int product; // Product ID (foreign key)
  final String productName;
  final double productPrice;
  final String? productImage;
  int quantity; // Quantity can be changed
  final double subtotal;

  CartItem({
    required this.id,
    required this.product,
    required this.productName,
    required this.productPrice,
    required this.productImage,
    required this.quantity,
    required this.subtotal,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['product_id'] ?? 0,
      product: json['product'] ?? 0,
      productName: json['product_name'] ?? 'Unknown Product',
      // FIX: Explicitly parse String to double, handle null
      productPrice:
          double.tryParse(json['product_price']?.toString() ?? '0.0') ?? 0.0,
      productImage: json['product_image'],
      quantity: json['quantity'] ?? 0,
      // FIX: Explicitly parse String to double, handle null
      subtotal: double.tryParse(json['subtotal']?.toString() ?? '0.0') ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'product': product,
      'product_name': productName,
      'product_price': productPrice,
      'quantity': quantity,
      'subtotal': subtotal,
    };
  }
}

class Cart {
  final int id;
  final int user;
  final List<CartItem> cartItems;
  final int totalItems;
  final double totalAmount;
  final DateTime createdAt;
  final DateTime updatedAt;

  Cart({
    required this.id,
    required this.user,
    required this.cartItems,
    required this.totalItems,
    required this.totalAmount,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Cart.fromJson(Map<String, dynamic> json) {
    var list = json['cart_items'] as List?;
    List<CartItem> cartItemsList = list != null
        ? list.map((i) => CartItem.fromJson(i)).toList()
        : [];

    return Cart(
      id: json['id'] ?? 0,
      user: json['user'] ?? 0,
      cartItems: cartItemsList,
      totalItems: json['total_items'] ?? 0,
      // FIX: Explicitly parse String to double for total_amount, handle null
      totalAmount:
          double.tryParse(json['total_amount']?.toString() ?? '0.0') ?? 0.0,
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      updatedAt: DateTime.tryParse(json['updated_at'] ?? '') ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user': user,
      'cart_items': cartItems.map((item) => item.toJson()).toList(),
      'total_items': totalItems,
      'total_amount': totalAmount,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}
