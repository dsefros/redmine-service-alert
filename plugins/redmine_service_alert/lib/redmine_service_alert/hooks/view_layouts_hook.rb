# frozen_string_literal: true

module RedmineServiceAlert
  module Hooks
    class ViewLayoutsHook < Redmine::Hook::ViewListener
      render_on :view_layouts_base_body_top, partial: 'service_alert/alert'

      def view_layouts_base_html_head(_context = {})
        stylesheet_link_tag('service_alert', plugin: 'redmine_service_alert') +
          javascript_include_tag('service_alert', plugin: 'redmine_service_alert')
      end
    end
  end
end
