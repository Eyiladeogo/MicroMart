// lib/models/product.dart

class Product {
  final int id;
  final String name;
  final String? description;
  final double price;
  final int stock;
  final String? imageUrl; // Changed from image to imageUrl

  Product({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    required this.stock,
    this.imageUrl,
  });

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: (json['id'] is int)
          ? json['id']
          : int.tryParse(json['id'].toString()) ?? 0,
      name: json['name'],
      description: json['description'],
      price: (json['price'] is int || json['price'] is double)
          ? (json['price'] as num).toDouble()
          : double.tryParse(json['price'].toString()) ?? 0.0,
      stock: (json['stock'] is int)
          ? json['stock']
          : int.tryParse(json['stock'].toString()) ?? 0,
      imageUrl: json['image'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'stock': stock,
      'image_url': imageUrl,
    };
  }
}
