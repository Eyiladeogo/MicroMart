// lib/widgets/product_card.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:micromart_frontend/models/product.dart';
import 'package:micromart_frontend/providers/auth_provider.dart';
import 'package:micromart_frontend/providers/cart_provider.dart';

class ProductCard extends StatelessWidget {
  final Product product;

  const ProductCard({super.key, required this.product});

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final cartProvider = Provider.of<CartProvider>(context, listen: false);

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: product.imageUrl != null && product.imageUrl!.isNotEmpty
                ? Image.network(
                    product.imageUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => Center(
                      child: Icon(
                        Icons.image_not_supported,
                        size: 50,
                        color: Colors.grey[400],
                      ),
                    ),
                  )
                : Center(
                    child: Icon(
                      Icons.image_not_supported,
                      size: 50,
                      color: Colors.grey[400],
                    ),
                  ),
          ),
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product.name,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.blueGrey,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  '\$${product.price.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.blueGrey[800],
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Stock: ${product.stock}',
                  style: TextStyle(
                    fontSize: 14,
                    color: product.stock > 0
                        ? Colors.green[700]
                        : Colors.red[700],
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 12),
                if (authProvider.isAuthenticated)
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: product.stock > 0
                          ? () async {
                              final success = await cartProvider.addToCart(
                                product.id,
                                1,
                              );
                              if (success) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      '${product.name} added to cart!',
                                    ),
                                  ),
                                );
                              } else {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      'Failed to add ${product.name} to cart. Not enough stock or other error.',
                                    ),
                                  ),
                                );
                              }
                            }
                          : null, // Disable button if out of stock
                      icon: const Icon(Icons.add_shopping_cart),
                      label: Text(
                        product.stock > 0 ? 'Add to Cart' : 'Out of Stock',
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: product.stock > 0
                            ? Colors.blueGrey[700]
                            : Colors.grey,
                      ),
                    ),
                  ),
                if (!authProvider.isAuthenticated)
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () {
                        // Optionally show a message or direct to login
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text(
                              'Please log in to add items to cart.',
                            ),
                          ),
                        );
                      },
                      icon: const Icon(Icons.login),
                      label: const Text('Login to Add'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.blueGrey[700],
                        side: BorderSide(color: Colors.blueGrey[700]!),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
