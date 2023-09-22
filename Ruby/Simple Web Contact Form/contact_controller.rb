# contact_controller.rb
class ContactController < ApplicationController
    def new
    end
  
    def create
      if contact_params[:message].blank?
        flash[:error] = "Please enter a message."
        redirect_to :back
      else
        ContactMailer.with(contact_params).new_message.deliver_now
        flash[:success] = "Your message has been sent."
        redirect_to root_path
      end
    end
  
    private
  
    def contact_params
      params.require(:contact).permit(:name, :email, :message)
    end
  end
  