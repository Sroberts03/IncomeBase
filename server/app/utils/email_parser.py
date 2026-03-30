def parse_email_to_html(raw_content: str, title: str = "Secure Portal Notification") -> str:
    """
    Takes plain text input with standard line breaks and wraps it uniformly 
    in a responsive, branded HTML format appropriate for standard email clients.
    """
    # Replace markdown-style or raw newlines with HTML line breaks
    formatted_text = raw_content.replace('\n', '<br>')
    
    html_wrapper = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
        <div style="background-color: #2563eb; padding: 24px; text-align: center;">
            <h1 style="color: #ffffff; margin: 0; font-size: 20px; font-weight: 600;">{title}</h1>
        </div>
        <div style="padding: 32px; background-color: #ffffff; color: #374151; font-size: 16px; line-height: 1.6;">
            {formatted_text}
        </div>
        <div style="background-color: #f9fafb; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb; font-size: 13px; color: #6b7280;">
            <p style="margin: 0;">This communication was securely routed via <strong>IncomeBase</strong></p>
        </div>
    </div>
    """
    
    return html_wrapper
