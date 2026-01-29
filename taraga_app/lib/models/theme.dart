/// Data model for Korean market themes
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
      id: json['id'] as int,
      name: json['name'] as String,
      keywords: (json['keywords'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
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
