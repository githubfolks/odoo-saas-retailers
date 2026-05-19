-- Seed data for 5 initial tenants
INSERT INTO tenants (tenant_id, business_name, whatsapp_number, razorpay_key, razorpay_secret, n8n_webhook_url)
VALUES 
('acme-corp', 'Acme Global Solutions', '919876543210', 'rzp_test_acme123', 'secret_acme_456', 'https://n8n.acme.com/webhook'),
('tech-flow', 'TechFlow Innovations', '919876543211', 'rzp_test_tech789', 'secret_tech_012', 'https://n8n.techflow.io/webhook'),
('green-retail', 'GreenLeaf Retailers', '919876543212', 'rzp_test_green345', 'secret_green_678', NULL),
('swift-logistics', 'Swift Logistics Group', '919876543213', 'rzp_test_swift901', 'secret_swift_234', 'https://n8n.swift.com/webhook'),
('urban-style', 'UrbanStyle Fashion', '919876543214', 'rzp_test_urban567', 'secret_urban_890', NULL);
