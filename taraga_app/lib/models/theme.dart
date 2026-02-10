class Theme {
  final int id;
  final String name;
  final List<String> keywords;

  Theme({
    required this.id,
    required this.name,
    required this.keywords,
  });

  factory Theme.fromJson(Map<String, dynamic> json) {
    return Theme(
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
