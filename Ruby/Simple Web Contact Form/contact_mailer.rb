# contact_mailer.rb
class ContactMailer < ApplicationMailer
    default from: "noreply@example.com"
  
    def new_message
      @name = params[:name]
      @email = params[:email]
      @message = params[:message]
  
      mail to: "youremail@example.com", subject: "New message from #{@name}"
    end
  end
  