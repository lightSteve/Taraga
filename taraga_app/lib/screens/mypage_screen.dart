import 'package:flutter/material.dart';
import 'package:flutter/cupertino.dart';
import '../services/api_service.dart';

class MyPageScreen extends StatefulWidget {
  const MyPageScreen({super.key});

  @override
  State<MyPageScreen> createState() => _MyPageScreenState();
}

class _MyPageScreenState extends State<MyPageScreen> {
  final ApiService _apiService = ApiService();
  final String _userUuid = "test_user_uuid"; // Mocked user ID
  
  List<dynamic> _watchlist = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadWatchlist();
  }

  Future<void> _loadWatchlist() async {
    setState(() => _isLoading = true);
    try {
      final list = await _apiService.getWatchlist(_userUuid);
      setState(() {
        _watchlist = list;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      print("Error loading watchlist: $e");
    }
  }

  Future<void> _addStock(String ticker, String name) async {
    try {
      await _apiService.addToWatchlist(_userUuid, ticker, name);
      _loadWatchlist(); // Refresh list
      if (mounted) Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  Future<void> _deleteStock(int id) async {
    try {
      await _apiService.removeFromWatchlist(id);
      _loadWatchlist(); // Refresh
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  void _showAddDialog() {
    showDialog(
      context: context,
      builder: (context) => const SearchStockDialog(),
    ).then((val) {
      if (val == true) {
        _loadWatchlist();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Page', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF1A1F3A),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile Header
            Row(
              children: [
                const CircleAvatar(
                  radius: 30,
                  backgroundColor: Colors.blueAccent,
                  child: Icon(Icons.person, size: 30, color: Colors.white),
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text("Guest User", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                    Text("Level 1 Investor", style: TextStyle(color: Colors.white54, fontSize: 14)),
                  ],
                )
              ],
            ),
            const SizedBox(height: 32),

            // Watchlist Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("My Watchlist", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                IconButton(
                  onPressed: _showAddDialog,
                  icon: const Icon(CupertinoIcons.add_circled, color: Colors.blueAccent),
                )
              ],
            ),
            const SizedBox(height: 16),

            _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _watchlist.isEmpty
                    ? Container(
                        padding: const EdgeInsets.all(32),
                        alignment: Alignment.center,
                        decoration: BoxDecoration(
                          color: const Color(0xFF1E1E2C),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Text("No stocks yet.\nAdd one to see insights!", textAlign: TextAlign.center, style: TextStyle(color: Colors.white54)),
                      )
                    : Column(
                        children: _watchlist.map((item) => _buildWatchlistItem(item)).toList(),
                      ),
          ],
        ),
      ),
    );
  }

  Widget _buildWatchlistItem(dynamic item) {
    return Dismissible(
      key: Key(item['id'].toString()),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        color: Colors.redAccent,
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      onDismissed: (direction) {
        _deleteStock(item['id']);
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: const Color(0xFF1E1E2C),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item['stock_name'], style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600)),
                Text(item['ticker'], style: const TextStyle(color: Colors.white54, fontSize: 12)),
              ],
            ),
            const Icon(Icons.notifications_active, color: Colors.amber, size: 20)
          ],
        ),
      ),
    );
  }
}

class SearchStockDialog extends StatefulWidget {
  const SearchStockDialog({super.key});

  @override
  State<SearchStockDialog> createState() => _SearchStockDialogState();
}

class _SearchStockDialogState extends State<SearchStockDialog> {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();
  List<dynamic> _searchResults = [];
  bool _isSearching = false;

  void _onSearchChanged(String query) async {
    if (query.isEmpty) {
      setState(() => _searchResults = []);
      return;
    }

    setState(() => _isSearching = true);
    try {
      final results = await _apiService.searchStock(query);
      setState(() {
        _searchResults = results;
        _isSearching = false;
      });
    } catch (e) {
      setState(() => _isSearching = false);
    }
  }

  Future<void> _addStock(Map<String, dynamic> stock) async {
    try {
      // Mock user UUID for MVP
      await _apiService.addToWatchlist("test_user_uuid", stock['ticker'], stock['name']);
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: const Color(0xFF1E1E2C),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        height: 400,
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text("Search Stock", style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            TextField(
              controller: _searchController,
              style: const TextStyle(color: Colors.white),
              onChanged: _onSearchChanged,
              decoration: InputDecoration(
                hintText: "Enter name or code (e.g. Samsung)",
                hintStyle: const TextStyle(color: Colors.white54),
                prefixIcon: const Icon(Icons.search, color: Colors.blueAccent),
                filled: true,
                fillColor: Colors.black12,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: _isSearching
                  ? const Center(child: CircularProgressIndicator())
                  : _searchResults.isEmpty
                      ? const Center(child: Text("No results", style: TextStyle(color: Colors.white38)))
                      : ListView.builder(
                          itemCount: _searchResults.length,
                          itemBuilder: (context, index) {
                            final stock = _searchResults[index];
                            return ListTile(
                              title: Text(stock['name'], style: const TextStyle(color: Colors.white)),
                              subtitle: Text(stock['ticker'], style: const TextStyle(color: Colors.white54)),
                              trailing: const Icon(Icons.add_circle_outline, color: Colors.blueAccent),
                              onTap: () => _addStock(stock),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}
