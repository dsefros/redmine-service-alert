# frozen_string_literal: true

require File.expand_path('lib/redmine_service_alert/hooks/view_layouts_hook', __dir__)

Redmine::Plugin.register :redmine_service_alert do
  name 'Redmine Service Alert plugin'
  author 'Codex'
  description 'Global incident alert banner and optional popup'
  version '0.1.0'
  requires_redmine version_or_higher: '5.0.0'

  settings default: {
    'enabled' => false,
    'severity' => 'info',
    'title' => '',
    'message' => '',
    'link_url' => '',
    'show_popup' => false,
    'version' => 0
  }, partial: nil
end
