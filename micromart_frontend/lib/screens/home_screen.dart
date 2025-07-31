// lib/screens/home_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:micromart_frontend/models/product.dart';
import 'package:micromart_frontend/providers/auth_provider.dart';
import 'package:micromart_frontend/services/api_service.dart';
import 'package:micromart_frontend/widgets/auth_modal.dart';
import 'package:micromart_frontend/widgets/product_card.dart';
import 'dart:math' as math; // Import for ceil

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  List<Product> _products = [];
  bool _isLoading = false;
  String? _errorMessage;
  int _currentPage = 1;
  int _totalPages = 1; // Initialize to 1
  final int _pageSize = 10; // Matches backend pagination
  final TextEditingController _searchController = TextEditingController();
  String _currentSearchQuery = '';
  String _currentOrdering = ''; // e.g., 'name', '-price'

  // Filter controllers
  final TextEditingController _minPriceController = TextEditingController();
  final TextEditingController _maxPriceController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchProducts();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _minPriceController.dispose();
    _maxPriceController.dispose();
    super.dispose();
  }

  Future<void> _fetchProducts({bool resetPage = false}) async {
    if (resetPage) {
      _currentPage = 1;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final Map<String, dynamic> responseData = await _apiService.getProducts(
        page: _currentPage,
        pageSize: _pageSize,
        search: _currentSearchQuery,
        ordering: _currentOrdering,
        minPrice: double.tryParse(_minPriceController.text),
        maxPrice: double.tryParse(_maxPriceController.text),
      );

      final List<Product> fetchedProducts = responseData['products'];
      final int totalCount = responseData['count'];

      setState(() {
        _products = fetchedProducts;
        _totalPages = (totalCount / _pageSize).ceil(); // Calculate total pages
        if (_totalPages == 0 && totalCount > 0) {
          // Handle case where count > 0 but less than page size
          _totalPages = 1;
        } else if (totalCount == 0) {
          _totalPages = 1; // If no products, still show 1 page
        }
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load products: $e';
        _isLoading = false;
      });
      debugPrint('Error fetching products: $e');
    }
  }

  void _showAuthModal(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return const AuthModal();
      },
    );
  }

  void _showProfileDropdown(BuildContext context, AuthProvider authProvider) {
    final RenderBox button = context.findRenderObject() as RenderBox;
    final RenderBox overlay =
        Overlay.of(context).context.findRenderObject() as RenderBox;
    final RelativeRect position = RelativeRect.fromRect(
      Rect.fromPoints(
        button.localToGlobal(Offset.zero, ancestor: overlay),
        button.localToGlobal(
          button.size.bottomRight(Offset.zero),
          ancestor: overlay,
        ),
      ),
      Offset.zero & overlay.size,
    );

    showMenu<String>(
      context: context,
      position: position,
      items: [
        PopupMenuItem(
          enabled: false, // Make this item non-clickable
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                authProvider.userPayload?['username'] ?? 'User',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                authProvider.userPayload?['email'] ?? '',
                style: TextStyle(color: Colors.grey[600], fontSize: 12),
              ),
            ],
          ),
        ),
        const PopupMenuDivider(),
        PopupMenuItem(
          value: 'logout',
          child: const Text('Logout'),
          onTap: () {
            Future.microtask(() => authProvider.logout());
          },
        ),
      ],
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Filter Products'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: _minPriceController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Min Price'),
              ),
              TextField(
                controller: _maxPriceController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Max Price'),
              ),
              DropdownButtonFormField<String>(
                value: _currentOrdering.isEmpty ? null : _currentOrdering,
                hint: const Text('Sort By'),
                items: const [
                  DropdownMenuItem(value: 'name', child: Text('Name (A-Z)')),
                  DropdownMenuItem(value: '-name', child: Text('Name (Z-A)')),
                  DropdownMenuItem(
                    value: 'price',
                    child: Text('Price (Low to High)'),
                  ),
                  DropdownMenuItem(
                    value: '-price',
                    child: Text('Price (High to Low)'),
                  ),
                  DropdownMenuItem(
                    value: 'stock',
                    child: Text('Stock (Low to High)'),
                  ),
                  DropdownMenuItem(
                    value: '-stock',
                    child: Text('Stock (High to Low)'),
                  ),
                ],
                onChanged: (value) {
                  setState(() {
                    _currentOrdering = value ?? '';
                  });
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                _minPriceController.clear();
                _maxPriceController.clear();
                setState(() {
                  _currentOrdering = '';
                });
                Navigator.of(context).pop();
                _fetchProducts(resetPage: true);
              },
              child: const Text('Clear Filters'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop();
                _fetchProducts(resetPage: true);
              },
              child: const Text('Apply Filters'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'MicroMart',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.shopping_cart_outlined),
            onPressed: () {
              Navigator.pushNamed(context, '/cart');
            },
          ),
          // Dynamic Profile/Sign-in Icon
          authProvider.isAuthenticated
              ? Builder(
                  builder: (context) => IconButton(
                    icon: const Icon(Icons.account_circle),
                    onPressed: () =>
                        _showProfileDropdown(context, authProvider),
                  ),
                )
              : IconButton(
                  icon: const Icon(Icons.login),
                  onPressed: () => _showAuthModal(context),
                ),
          const SizedBox(width: 10),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60.0),
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 8.0,
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search products...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                setState(() {
                                  _currentSearchQuery = '';
                                });
                                _fetchProducts(resetPage: true);
                              },
                            )
                          : null,
                    ),
                    onSubmitted: (value) {
                      setState(() {
                        _currentSearchQuery = value;
                      });
                      _fetchProducts(resetPage: true);
                    },
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.filter_list),
                  onPressed: _showFilterDialog,
                  tooltip: 'Filter & Sort',
                ),
              ],
            ),
          ),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(_errorMessage!, textAlign: TextAlign.center),
                  const SizedBox(height: 10),
                  ElevatedButton(
                    onPressed: _fetchProducts,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : _products.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.sentiment_dissatisfied,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'No products found!',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Try adjusting your search or filters.',
                    style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: () {
                      _searchController.clear();
                      _minPriceController.clear();
                      _maxPriceController.clear();
                      setState(() {
                        _currentSearchQuery = '';
                        _currentOrdering = '';
                      });
                      _fetchProducts(resetPage: true);
                    },
                    child: const Text('Show All Products'),
                  ),
                ],
              ),
            )
          : RefreshIndicator(
              onRefresh: () => _fetchProducts(resetPage: true),
              child: GridView.builder(
                padding: const EdgeInsets.all(16.0),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 0.7,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                ),
                itemCount: _products.length,
                itemBuilder: (context, index) {
                  return ProductCard(product: _products[index]);
                },
              ),
            ),
      bottomNavigationBar: _products.isNotEmpty && _totalPages > 1
          ? Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back),
                    onPressed: _currentPage > 1
                        ? () {
                            setState(() {
                              _currentPage--;
                            });
                            _fetchProducts();
                          }
                        : null,
                  ),
                  Text('Page $_currentPage of $_totalPages'),
                  IconButton(
                    icon: const Icon(Icons.arrow_forward),
                    onPressed: _currentPage < _totalPages
                        ? () {
                            setState(() {
                              _currentPage++;
                            });
                            _fetchProducts();
                          }
                        : null,
                  ),
                ],
              ),
            )
          : null,
    );
  }
}
