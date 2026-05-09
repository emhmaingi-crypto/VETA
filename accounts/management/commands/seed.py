from django.core.management.base import BaseCommand
from accounts.models import StudentUser
from opportunities.models import Opportunity, PartnerOrganisation, Application
from mentorship.models import Mentor, MentorshipRequest
from scholarships.models import Scholarship
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed initial VETA Connect data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')

        StudentUser.objects.filter(username='student1').delete()
        user = StudentUser.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='veta1234',
            first_name='Amina',
            last_name='Mwangi',
            institution='Nairobi Technical College',
            county='Nairobi',
            course='Electrical Engineering',
            level='diploma',
            graduation_year=2026,
            skills='electrical systems, automation, teamwork',
            bio='TVET student passionate about renewable energy and hands-on innovation.',
        )

        PartnerOrganisation.objects.all().delete()
        mentors = Mentor.objects.all()
        scholarships = Scholarship.objects.all()
        opportunities = Opportunity.objects.all()
        Application.objects.all().delete()
        MentorshipRequest.objects.all().delete()

        partner1 = PartnerOrganisation.objects.create(
            name='Green Future Energy',
            type='Industry Partner',
            website='https://greenfuture.example.com',
            description='A renewable energy company hiring technicians and trainees.',
            contact_email='recruitment@greenfuture.example.com',
            county='Nairobi',
            is_verified=True,
        )
        partner2 = PartnerOrganisation.objects.create(
            name='Digital Skills Hub',
            type='Training Partner',
            website='https://digitalskillshub.example.com',
            description='A tech incubator looking for IT apprentices and interns.',
            contact_email='hello@digitalskillshub.example.com',
            county='Nakuru',
            is_verified=True,
        )

        Opportunity.objects.create(
            partner=partner1,
            title='Electrical Maintenance Technician Apprentice',
            type='apprenticeship',
            description='Join a hands-on team maintaining solar installations across Nairobi.',
            requirements='Basic electrical knowledge, willingness to learn, safety-focused.',
            skills_required='electrical systems, maintenance, teamwork',
            level_required='diploma',
            county='Nairobi',
            stipend='KES 18,000 / month',
            duration='6 months',
            deadline=timezone.now().date().replace(day=30),
            slots=4,
            is_active=True,
        )
        Opportunity.objects.create(
            partner=partner2,
            title='IT Support Internship',
            type='internship',
            description='Build your IT support and customer service experience with a digital hub.',
            requirements='Good communication skills, curiosity about networks and hardware.',
            skills_required='IT support, troubleshooting, communication',
            level_required='certificate',
            county='Nakuru',
            stipend='KES 12,000 / month',
            duration='3 months',
            deadline=timezone.now().date().replace(day=25),
            slots=5,
            is_active=True,
        )

        Mentor.objects.create(
            name='Faith Wanjiru',
            title='Robotics Trainer',
            organisation='TVET Innovation Lab',
            bio='Faith mentors students in robotics, automation, and product design.',
            expertise='robotics, innovation, prototyping, presentation skills',
            email='faith@example.com',
            linkedin_url='https://www.linkedin.com/in/faith-wanjiru',
            slots_available=4,
            is_active=True,
        )
        Mentor.objects.create(
            name='Peter Okello',
            title='Green Tech Entrepreneur',
            organisation='EcoBuild Solutions',
            bio='Peter supports learners exploring climate-smart solutions and commercialization.',
            expertise='green technology, entrepreneurship, market access',
            email='peter@example.com',
            linkedin_url='https://www.linkedin.com/in/peter-okello',
            slots_available=3,
            is_active=True,
        )

        Scholarship.objects.create(
            title='TVET Excellence Scholarship',
            provider='Kenya Skills Fund',
            description='Full scholarship for TVET students focusing on green innovation and research.',
            eligibility='Open to diploma and higher diploma students with strong academic records.',
            amount='KES 150,000',
            level='diploma',
            deadline=timezone.now().date().replace(day=20),
            apply_url='https://kenyaskillsfund.example.com/apply',
            is_active=True,
        )
        Scholarship.objects.create(
            title='Women in Tech Award',
            provider='STEM Growth Alliance',
            description='Award and mentorship package for women pursuing digitalization and robotics.',
            eligibility='Female students in TVET programs from certificate to higher diploma.',
            amount='KES 100,000',
            level='certificate',
            deadline=timezone.now().date().replace(day=28),
            apply_url='https://stemgrowth.example.com/women-in-tech',
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS('Seed data created successfully.'))
