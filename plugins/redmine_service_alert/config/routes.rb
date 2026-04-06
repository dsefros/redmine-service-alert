# frozen_string_literal: true

post 'service_alert/activate', to: 'service_alert#activate'
post 'service_alert/deactivate', to: 'service_alert#deactivate'
get 'service_alert/current', to: 'service_alert#current'
