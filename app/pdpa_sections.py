"""
Reference data for the 8 PDPA obligations this system checks for.

Each obligation has:
- anchor_phrases: several well-formed example sentences that represent what
  "satisfying this obligation" sounds like. These get embedded and used as
  the semantic target for comparison. Having MULTIPLE anchors per section
  (rather than one) matters a lot -- it lets the model recognise different
  phrasings of the same legal idea, instead of over-fitting to one wording.
- keywords: concrete words/phrases that a sentence should contain if it is
  genuinely addressing this obligation (not just "sounding privacy-related").
  This is the second half of the hybrid check.

Source: Sri Lanka Personal Data Protection Act, No. 9 of 2022.
"""

PDPA_SECTIONS = [
    {
        "id": "transparency",
        "section_number": "Section 11",
        "title": "Transparency",
        "description": "The controller must provide information about data processing in a clear, transparent, and accessible way, including how to contact the organisation.",
        "anchor_phrases": [
            "This privacy policy explains clearly how we collect, use, and process your personal data.",
            "We provide transparent information about our data processing practices in plain language.",
            "You can contact our Data Protection Officer using the details provided in this policy.",
            "This document describes what personal information we collect and why we collect it.",
        ],
        "keywords": [
            "privacy policy", "privacy notice", "data protection officer", "data privacy officer",
            "privacy officer", "dpo", "contact us", "how we use your data", "how we collect",
            "transparent", "transparency",
        ],
    },
    {
        "id": "consent_withdrawal",
        "section_number": "Section 14",
        "title": "Withdrawal of Consent",
        "description": "Users must be able to withdraw previously given consent at any time, and must be told how to do so.",
        "anchor_phrases": [
            "You may withdraw your consent to data processing at any time.",
            "You can unsubscribe from our communications or opt out whenever you wish.",
            "If you no longer wish us to process your data, you may revoke your consent by contacting us.",
            "Users are free to opt out of marketing communications at any point.",
        ],
        "keywords": [
            "withdraw", "revoke", "opt out", "opt-out", "unsubscribe",
            "stop processing", "cancel marketing", "cancel your",
        ],
    },
    {
        "id": "right_to_erasure",
        "section_number": "Section 16",
        "title": "Right to Erasure",
        "description": "Users must be able to request deletion of their personal data, and the policy should explain how.",
        "anchor_phrases": [
            "You may request that we permanently delete your personal data.",
            "Users have the right to ask us to erase their personal information from our systems.",
            "You can request removal of your account and all associated personal data.",
            "To delete your data, please contact our support team with your request.",
        ],
        "keywords": [
            # Bare "delet"/"eras"/"remov" stems were removed on purpose.
            # "We will delete your personal information when it is no
            # longer needed" (Sampath) and "Personal data will be deleted
            # as soon as it is no longer necessary" (Dialog) both contain
            # those stems, but they're the company describing its OWN
            # retention-driven auto-deletion schedule -- not a right the
            # user can invoke. Every phrase below requires the deletion to
            # be something the user requests/asks for/initiates, so a
            # retention clause can no longer trigger a false "compliant".
            "request deletion", "request erasure", "request removal",
            "request that we", "request us to",
            "request that we delete", "request that we erase", "requested to delete",
            "ask us to delete", "ask us to erase", "ask to erase", "ask to delete",
            "wish to delete", "you may delete your", "you can delete your",
            "right to be forgotten", "right to erasure",
            "deletion:", "with your request",
        ],
    },
    {
        "id": "right_to_access",
        "section_number": "Section 13",
        "title": "Right to Access",
        "description": "Users must be able to request access to, or a copy of, the personal data held about them.",
        "anchor_phrases": [
            "You may request a copy of the personal data we hold about you.",
            "Users can view and access the information we have collected about them.",
            "You have the right to request access to your personal data at any time.",
            "You can ask us for details of what personal information we store about you.",
        ],
        "keywords": [
            # Bare "access" and direction-ambiguous phrases like "access
            # your data" were removed on purpose. "We may collect or access
            # your personal data" (a data-collection clause, Dialog) and "we
            # restrict access to personal data" (a security clause, Google)
            # both contain "access your"/"access to" but mean the OPPOSITE
            # of a user's right of access -- the company is the one doing
            # the accessing, not the user. Every phrase below requires
            # you/your to be the one requesting, holding, or exercising the
            # access -- not the object of someone else's access.
            "copy of your data", "copy of the personal data", "copy of your personal data",
            "right to access", "you may access", "you can access",
            "you have the right to access", "you have access to your",
            "your right to access", "request access to your",
            "right to request access", "you can request access",
            "provide you with a copy", "provide you a copy", "obtain a copy of your",
            "obtain your personal data", "view your data", "view and access", "request access",
            "data subject access", "confirm the existence of processing",
            "confirm whether we are processing", "right to know", "know and access",
        ],
    },
    {
        "id": "data_accuracy",
        "section_number": "Section 8",
        "title": "Data Accuracy & Updates",
        "description": "Personal data must be kept accurate and up to date, and users should be able to correct errors.",
        "anchor_phrases": [
            "You may update or correct your personal information at any time.",
            "We take reasonable steps to ensure your personal data remains accurate and up to date.",
            "If any of your details are incorrect, you can request a correction.",
            "You can edit your account information to keep it accurate.",
        ],
        "keywords": [
            "correct", "rectif", "update your", "inaccura", "accuracy of data",
            "keep your data accurate", "update or correct",
        ],
    },
    {
        "id": "data_retention",
        "section_number": "Section 9",
        "title": "Data Retention",
        "description": "Personal data should not be retained for longer than necessary, and the retention period should be disclosed.",
        "anchor_phrases": [
            "We retain your personal data only for as long as necessary to fulfil the purposes described in this policy.",
            "Your data will be stored for a specific period of time, after which it will be deleted.",
            "We keep personal information for a maximum of a defined retention period before disposal.",
            "Data is not kept longer than required by law or business necessity.",
        ],
        "keywords": [
            "retent", "retain", "how long we keep", "how long we store",
            "storage period", "no longer than necessary", "ongoing legitimate need",
            "for as long as",
        ],
    },
    {
        "id": "security",
        "section_number": "Section 10",
        "title": "Security & Protection",
        "description": "Appropriate technical and organisational security measures (e.g. encryption, access control) must be used to protect personal data.",
        "anchor_phrases": [
            "We use encryption and access controls to protect your personal data from unauthorised access.",
            "Appropriate technical and organisational security measures are in place to safeguard your information.",
            "Your data is protected using industry-standard security practices such as encryption in transit and at rest.",
            "We restrict access to personal data to authorised personnel only.",
        ],
        "keywords": [
            "encrypt", "access control", "secur", "protect your data", "protect your information",
            "safeguard", "authoris", "authoriz", "technical and organi", "prevent unauthor",
        ],
    },
    {
        "id": "cross_border_transfer",
        "section_number": "Section 26",
        "title": "Cross-Border Data Transfer",
        "description": "Any transfer of personal data outside Sri Lanka must be disclosed and must follow the rules for international transfer.",
        "anchor_phrases": [
            "Your personal data may be transferred to and processed in countries outside Sri Lanka.",
            "We may share your information with third-party service providers located in other countries.",
            "Data may be stored on servers located outside of Sri Lanka.",
            "Any international transfer of your data is carried out in compliance with applicable data protection laws.",
        ],
        "keywords": [
            "outside sri lanka", "cross-border", "cross border", "international transfer",
            "transferred to other countries", "servers located in", "third-party countries",
            "located outside",
        ],
    },
]