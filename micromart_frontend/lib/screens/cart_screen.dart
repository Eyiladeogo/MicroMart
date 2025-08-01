// lib/screens/cart_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:micromart_frontend/providers/cart_provider.dart';

class CartScreen extends StatelessWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your Cart')),
      body: Consumer<CartProvider>(
        builder: (context, cartProvider, child) {
          if (cartProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final cart = cartProvider.cart;

          if (cart == null || cart.cartItems.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.shopping_cart_outlined,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Your cart is empty!',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Start adding some amazing products.',
                    style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () {
                      Navigator.of(context).pop(); // Go back to home screen
                    },
                    child: const Text('Browse Products'),
                  ),
                ],
              ),
            );
          }

          return Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16.0),
                  itemCount: cart.cartItems.length,
                  itemBuilder: (context, index) {
                    final item = cart.cartItems[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Row(
                          children: [
                            // Product Image (Placeholder or actual image)
                            Container(
                              width: 80,
                              height: 80,
                              decoration: BoxDecoration(
                                color: Colors.grey[200],
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child:
                                  item.productImage != null &&
                                      item.productImage!.isNotEmpty
                                  ? Image.network(
                                      item.productImage!,
                                      fit: BoxFit.cover,
                                      errorBuilder:
                                          (context, error, stackTrace) =>
                                              Center(
                                                child: Icon(
                                                  Icons.image_not_supported,
                                                  size: 40,
                                                  color: Colors.grey[400],
                                                ),
                                              ),
                                    )
                                  : Center(
                                      child: Icon(
                                        Icons.image_not_supported,
                                        size: 40,
                                        color: Colors.grey[400],
                                      ),
                                    ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    item.productName,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.blueGrey,
                                    ),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '₦${item.productPrice.toStringAsFixed(2)}',
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: Colors.blueGrey[800],
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Row(
                                    children: [
                                      IconButton(
                                        icon: const Icon(
                                          Icons.remove_circle_outline,
                                        ),
                                        onPressed: () async {
                                          await cartProvider.adjustItemQuantity(
                                            item.id,
                                            'decrement',
                                            1,
                                          );
                                        },
                                      ),
                                      Text(
                                        '${item.quantity}',
                                        style: const TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      IconButton(
                                        icon: const Icon(
                                          Icons.add_circle_outline,
                                        ),
                                        onPressed: () async {
                                          await cartProvider.adjustItemQuantity(
                                            item.id,
                                            'increment',
                                            1,
                                          );
                                        },
                                      ),
                                      const Spacer(),
                                      Text(
                                        'Subtotal: ₦${item.subtotal.toStringAsFixed(2)}',
                                        style: const TextStyle(
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                            // IconButton(
                            //   icon: const Icon(
                            //     Icons.delete_outline,
                            //     color: Colors.red,
                            //   ),
                            //   onPressed: () async {
                            //     final success = await cartProvider
                            //         .removeFromCart(item.id);
                            //     if (success) {
                            //       ScaffoldMessenger.of(context).showSnackBar(
                            //         SnackBar(
                            //           content: Text(
                            //             '${item.productName} removed from cart.',
                            //           ),
                            //         ),
                            //       );
                            //     } else {
                            //       ScaffoldMessenger.of(context).showSnackBar(
                            //         SnackBar(
                            //           content: Text(
                            //             'Failed to remove ${item.productName}.',
                            //           ),
                            //         ),
                            //       );
                            //     }
                            //   },
                            // ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Total Items:',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        Text(
                          '${cart.totalItems}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Total Amount:',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '₦${cart.totalAmount.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.blueGrey,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () async {
                          final success = await cartProvider.placeOrder();
                          if (success) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Order placed successfully!'),
                              ),
                            );
                            Navigator.of(
                              context,
                            ).pop(); // Go back to home after order
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text(
                                  'Failed to place order. Check stock or try again.',
                                ),
                              ),
                            );
                          }
                        },
                        icon: const Icon(Icons.payment),
                        label: const Text('Place Order'),
                      ),
                    ),
                    const SizedBox(height: 10),
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          final success = await cartProvider.clearCart();
                          if (success) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Cart cleared.')),
                            );
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                content: Text('Failed to clear cart.'),
                              ),
                            );
                          }
                        },
                        icon: const Icon(Icons.delete_sweep),
                        label: const Text('Clear Cart'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
