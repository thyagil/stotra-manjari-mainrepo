class ProjectSummary {
  final String id;        // e.g. "ramayanam_sriramghanapatigal"
  final String title;
  final String subtitle;
  final String thumbnail;
  final bool isPremium;

  ProjectSummary({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.thumbnail,
    required this.isPremium,
  });

  factory ProjectSummary.fromJson(Map<String, dynamic> json) {
    return ProjectSummary(
      id: json['code'] ?? json['id'],
      title: json['title'] ?? '',
      subtitle: json['subtitle'] ?? '',
      thumbnail: json['thumbnail'] ?? '',
      isPremium: json['monetization']?['isPremium'] ?? false,
    );
  }
}

class ProjectMetadata {
  final String id;
  final String title;
  final String description;
  final String type;
  final List<VolumeInfo> volumes;

  ProjectMetadata({
    required this.id,
    required this.title,
    required this.description,
    required this.type,
    required this.volumes,
  });

  factory ProjectMetadata.fromJson(Map<String, dynamic> json) {
    return ProjectMetadata(
      id: json['code'] ?? json['id'],
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      type: json['type'] ?? 'volumeBased',
      volumes: (json['volumes'] as List<dynamic>? ?? [])
          .map((v) => VolumeInfo.fromJson(v))
          .toList(),
    );
  }
}

class VolumeInfo {
  final int index;
  final String name;
  final int chapterCount; // <-- integer, matches your JSON
  final int state; // 0=hidden, 1=coming soon, 2=enabled

  const VolumeInfo({
    required this.index,
    required this.name,
    required this.chapterCount,
    required this.state,
  });

  factory VolumeInfo.fromJson(Map<String, dynamic> json) {
    return VolumeInfo(
      index: json['index'] ?? 0,
      name: json['name'] ?? '',
      chapterCount: json['chapters'] ?? 0, // <-- int, e.g. 77
      state: json['state'] ?? 2, // default to enabled
    );
  }
  bool get isHidden => state == 0;
  bool get isComingSoon => state == 1;
  bool get isEnabled => state == 2;
}
