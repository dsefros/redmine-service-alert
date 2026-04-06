# frozen_string_literal: true

class ServiceAlertController < ApplicationController
  skip_before_action :verify_authenticity_token
  before_action :authenticate_token!

  VALID_SEVERITIES = %w[info warning critical].freeze

  def activate
    payload = parse_payload
    severity = payload['severity'].to_s

    unless VALID_SEVERITIES.include?(severity)
      render json: { error: 'invalid_severity', allowed: VALID_SEVERITIES }, status: :unprocessable_entity
      return
    end

    settings = merged_settings
    version = settings['version'].to_i + 1

    settings['enabled'] = true
    settings['severity'] = severity
    settings['title'] = payload['title'].to_s
    settings['message'] = payload['message'].to_s
    settings['link_url'] = payload['link_url'].to_s
    settings['show_popup'] = truthy?(payload['show_popup'])
    settings['version'] = version

    save_settings(settings)

    render json: current_state(settings), status: :ok
  end

  def deactivate
    settings = merged_settings
    settings['enabled'] = false

    save_settings(settings)

    render json: current_state(settings), status: :ok
  end

  def current
    render json: current_state(merged_settings), status: :ok
  end

  private

  def authenticate_token!
    expected = ENV['REDMINE_SERVICE_ALERT_TOKEN'].to_s
    provided = request.headers['X-Service-Alert-Token'].to_s

    if expected.empty? || provided.empty? || !ActiveSupport::SecurityUtils.secure_compare(provided, expected)
      render json: { error: 'unauthorized' }, status: :unauthorized
      nil
    end
  end

  def parse_payload
    return {} if request.body.blank?

    JSON.parse(request.body.read)
  rescue JSON::ParserError
    {}
  end

  def merged_settings
    defaults = Redmine::Plugin.find(:redmine_service_alert).settings[:default]
    defaults.merge(Setting.plugin_redmine_service_alert || {})
  end

  def save_settings(settings)
    Setting.plugin_redmine_service_alert = settings
  end

  def current_state(settings)
    {
      enabled: truthy?(settings['enabled']),
      severity: settings['severity'].to_s,
      title: settings['title'].to_s,
      message: settings['message'].to_s,
      link_url: settings['link_url'].to_s,
      show_popup: truthy?(settings['show_popup']),
      version: settings['version'].to_i
    }
  end

  def truthy?(value)
    value == true || value.to_s == 'true' || value.to_s == '1'
  end
end
