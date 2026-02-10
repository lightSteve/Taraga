class MarketTheme {
  final int id;
  final String name;
  final List<String> keywords;

  MarketTheme({
    required this.id,
    required this.name,
    required this.keywords,
  });

  factory MarketTheme.fromJson(Map<String, dynamic> json) {
    return MarketTheme(
      id: json['id'],
      name: json['name'] ?? '',
      keywords: (json['keywords'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'keywords': keywords,
    };
  }
}
