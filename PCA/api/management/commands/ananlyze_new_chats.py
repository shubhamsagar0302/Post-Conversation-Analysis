from django.core.management.base import BaseCommand
from api.models import Conversation
from api.services.analysis_service import perform_analysis
import sys

class Command(BaseCommand):
    help = 'Performs post-conversation analysis on all new conversations without analysis.'

    def handle(self, *args, **options):
        # Find all conversations that do NOT have an analysis object 
        new_conversations = Conversation.objects.filter(analysis__isnull=True)
        
        if not new_conversations.exists():
            self.stdout.write(self.style.SUCCESS('No new conversations to analyze.'))
            return

        self.stdout.write(f'Found {new_conversations.count()} new conversations to analyze...')
        
        success_count = 0
        fail_count = 0
        
        for conversation in new_conversations:
            try:
                perform_analysis(conversation.id)
                success_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to analyze conversation {conversation.id}: {e}'))
                fail_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully analyzed {success_count} conversations.'))
        if fail_count > 0:
            self.stdout.write(self.style.WARNING(f'Failed to analyze {fail_count} conversations.'))

def run_analysis():
    """
    A dedicated function to be called by django-crontab.
    This avoids issues with stdout/stderr pipes in cron.
    """
    print("Cron Job: Starting analysis of new chats...")
    try:
        # Find all conversations that do NOT have an analysis object
        new_conversations = Conversation.objects.filter(analysis__isnull=True)
        
        if not new_conversations.exists():
            print("Cron Job: No new conversations to analyze.")
            return

        print(f"Cron Job: Found {new_conversations.count()} new conversations...")
        
        count = 0
        for conversation in new_conversations:
            try:
                perform_analysis(conversation.id)
                count += 1
            except Exception as e:
                print(f"Cron Job ERROR: Failed on conversation {conversation.id}: {e}", file=sys.stderr)
        
        print(f"Cron Job: Successfully analyzed {count} conversations.")
    except Exception as e:
        print(f"Cron Job CRITICAL: {e}", file=sys.stderr)
