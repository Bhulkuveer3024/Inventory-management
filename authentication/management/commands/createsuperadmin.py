import BaseCommand
from authentication.models import CustomUser

class Command(BaseCommand):
    help = 'Create a system administrator with full admin access'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for the system administrator')
        parser.add_argument('email', type=str, help='Email for the system administrator')
        parser.add_argument('--password', type=str, help='Password (will prompt if not provided)')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password')
        
        # Check if user already exists
        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists!')
            )
            return
        
        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email "{email}" already exists!')
            )
            return
        
        # Get password if not provided
        if not password:
            password = self.get_password()
        
        # Create the system administrator
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='system_admin'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created system administrator "{username}" with full admin access!'
            )
        )
        self.stdout.write(f'User can now access Django admin at /admin/')
        self.stdout.write(f'Login with username: {username}')

    def get_password(self):
        import getpass
        while True:
            password = getpass.getpass('Enter password: ')
            password_confirm = getpass.getpass('Confirm password: ')
            if password == password_confirm:
                return password
            else:
                self.stdout.write(self.style.ERROR('Passwords do not match. Try again.'))
