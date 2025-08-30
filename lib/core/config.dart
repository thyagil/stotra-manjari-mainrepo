/// Toggle this flag to switch between local testing and production
const bool useLocal = true;

/// Base URL for remote projects (Google Cloud)
const String remoteProjectsRoot =
    "https://storage.googleapis.com/stotra-manjari-assets/projects"; // no trailing slash

/// Path to local assets
const String localProjectsRoot =
    "https://stotras.synology.me/stotra-manjari-assets/projects"; // no trailing slash

/// Always use this getter to build paths
String get baseProjectsRoot =>
    useLocal ? localProjectsRoot : remoteProjectsRoot;
