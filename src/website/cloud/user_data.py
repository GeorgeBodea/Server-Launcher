from flask import render_template

class UserDataManager:
    def __init__(self, template_path='user_data.sh.j2'):
        self.template_path = template_path

    def generate_user_data_script(self, tool_selections):
        """
        Generates the User Data script based on the tool selections.

        Parameters:
            tool_selections (list): List of selected tools and versions.

        Returns:
            str: Rendered User Data script with proper encoding and line endings.
        """
        
        if tool_selections:
            try:
                rendered_script = render_template(self.template_path,
                                                  tool_selections=tool_selections)
                
                # Ensure Unix line endings
                rendered_script = rendered_script.replace('\r\n', '\n')

                return rendered_script
            except Exception as e:
                print(f"Error rendering User Data script: {e}")
                raise e
        else:
            return ""
