% PUFGuard policy-support rules.
% Rates are encoded as integer basis points (10000 = 100%).
% These rules generate explainable research recommendations; they are not law.
% The program is fail-closed: missing profile facts make the program
% unsatisfiable, and the pipeline treats an empty result as an error.

% --- Stratum 0: Profile completeness ---
% A dataset must supply all three metric atoms before any decision can be derived.
% If any required fact is missing, the integrity constraint below fires and
% the solver produces no stable model, causing the pipeline to halt.

profile_complete(D) :- dataset(D), singleton_bp(D,_), below_k5_bp(D,_), homogeneous_bp(D,_).

:- dataset(D), not profile_complete(D).

% --- Stratum 1: Risk-level classification ---

high_linkability(D) :- dataset(D), singleton_bp(D,P), threshold(singleton_high,T), P >= T.
medium_linkability(D) :- dataset(D), singleton_bp(D,P), threshold(singleton_medium,L), threshold(singleton_high,H), P >= L, P < H.
low_linkability(D) :- dataset(D), singleton_bp(D,P), threshold(singleton_medium,T), P < T.

high_small_group_exposure(D) :- dataset(D), below_k5_bp(D,P), threshold(below_k5_high,T), P >= T.
high_attribute_disclosure(D) :- dataset(D), sensitive(D), homogeneous_bp(D,P), threshold(homogeneous_high,T), P >= T.

% --- Stratum 2: Flag generation ---

flag(D,structural_identifier_present) :- structural_identifier(D).
flag(D,free_text_present) :- free_text(D).
flag(D,high_linkability) :- high_linkability(D).
flag(D,medium_linkability) :- medium_linkability(D).
flag(D,high_small_group_exposure) :- high_small_group_exposure(D).
flag(D,high_attribute_disclosure) :- high_attribute_disclosure(D), sensitive(D).

% --- Stratum 3: Recommended actions ---

action(D,remove_structural_identifiers) :- structural_identifier(D).
action(D,redact_or_model_free_text) :- free_text(D).
action(D,generalize_quasi_identifiers) :- high_linkability(D).
action(D,compare_auxiliary_knowledge) :- high_linkability(D).
action(D,enforce_sensitive_value_diversity) :- high_attribute_disclosure(D), sensitive(D).
action(D,document_threat_model) :- dataset(D).

% --- Stratum 4: Decision synthesis ---
% Restricted review has highest precedence.
% Structural identifiers and free text independently trigger restriction,
% regardless of whether a sensitive attribute is declared.

restricted_review(D) :- structural_identifier(D).
restricted_review(D) :- free_text(D).
restricted_review(D) :- sensitive(D), high_linkability(D), high_attribute_disclosure(D).

remediation_needed(D) :- dataset(D), not restricted_review(D), high_linkability(D).
remediation_needed(D) :- dataset(D), not restricted_review(D), high_small_group_exposure(D).
remediation_needed(D) :- dataset(D), not restricted_review(D), high_attribute_disclosure(D).

public_candidate(D) :- dataset(D), not restricted_review(D), not remediation_needed(D).

decision(D,restricted_review) :- restricted_review(D).
decision(D,remediate_before_release) :- remediation_needed(D).
decision(D,public_candidate_after_documented_review) :- public_candidate(D).

% --- Integrity constraints ---

% Exactly one metric value per dataset per measure.
:- dataset(D), #count { P : singleton_bp(D,P) } != 1.
:- dataset(D), #count { P : below_k5_bp(D,P) } != 1.
:- dataset(D), #count { P : homogeneous_bp(D,P) } != 1.

% Exactly one threshold value per parameter.
:- #count { T : threshold(singleton_high,T) } != 1.
:- #count { T : threshold(singleton_medium,T) } != 1.
:- #count { T : threshold(below_k5_high,T) } != 1.
:- #count { T : threshold(homogeneous_high,T) } != 1.

% Threshold ordering: medium < high for singleton.
:- threshold(singleton_medium,L), threshold(singleton_high,H), L >= H.

% Exactly one decision per dataset.
:- dataset(D), not decision(D,_).
:- dataset(D), decision(D,C1), decision(D,C2), C1 != C2.

#show decision/2.
#show action/2.
#show flag/2.
