import os
from flask import Flask, request, jsonify, render_template
from google import genai # User's specified import
from google.genai import types # User's specified import
import PyPDF2
import docx # for python-docx
import re
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


study_material = """CIVIL PLEADINGS

1. Suit for recovery under Order XXXVII of the Code of Civil Procedure 1908 
2. Draft Affidavit
3. Suit for Permanent Injunction
4. Application for Temporary Injunction Under Order XXXIX Rules 1 and 2 of the Code of Civil Procedure, 1908
5. Application under Order XXXIX, Rule 2-A of the Code of Civil Procedure, 1908
6. Application under Order XXXIII read with Section 151 of the Code of Civil Procedure to sue as an Indigent Person
7. Suit for Ejectment and Damages for Wrongful Use and Occupation
8. Suit for Specific Performance of Contract
9. Model Draft Written Statement
10. Caveat under section 148-A of the Code of Civil Procedure, 1908
11. Transfer Petition (Civil) U/s 25 of the Civil Procedure Code, 1908
12. Application for the Execution of Decree

MATRIMONIAL PLEADINGS

13. Petitions under the Matrimonial Pleadings-Introduction
14. Petition for Restitution of Conjugal Rights under Section 9 of the Hindu Marriage Act, 1955
15. Petition for Judicial Separation under Section 10 of the Hindu Marriage Act, 1955
16. Petition for Dissolution of Marriage by Decree of Divorce under Section 13 of the Hindu Marriage Act, 1955
17. Petition for Dissolution of Marriage by Decree of Divorce under Section 13B(1) of the Hindu Marriage Act, 1955
18. Draft affidavit for matrimonial pleadings
PLEADINGS UNDER INDIAN SUCCESSION ACT, 192519. Petition for Grant of Probate in High Court
20. Petition for Grant of Letters of Administration
21. Petition for Grant of Succession Certificate
PETITONS UNDER CONSTITUTIONAL LAW
22. Writ Petition- Meaning
23. Writ Petition under Article 226 of the Constitution of India
24. Writ Petition (Cri.) for Enforcement of Fundamental Rights
25. Special Leave Petition (Civil) under Article 136 of the Constitution of India
26. Special Leave Petition (Criminal ) under Article 136 of the Constitution of India

PLEADINGS UNDER CRIMINAL LAW

27. Application for Regular Bail
28. Application for Anticipatory Bail
29. Complaint under section 138 of the Negotiable Instruments Act, 1881
30. Application under section 125 of the Code of Criminal Procedure, 1972

OTHER MISCELLANEOUS PLEADINGS

31. Complaint under Section 12 of Consumer Protection Act, 1986
32. Contempt Petition under Section 11 and 12 of The Contempt of Courts Act, 1971
33. Petition under section 12 of Domestic Violence Act, 2005


# DRAFTING RULES \& SKILLS 

Drafting in general means, putting one's own ideas in writing. Drafting of any matter is an art. Drafting of legal matters requires greater skills and efficiencies. It requires thorough knowledge of law, procedure, settled judicial principles, besides proficiency in English language. A perfect drafting of matters in relation to suits, applications, complaints, writ petition, appeals, revision, reviews and other such matters connected therewith shall obviously lead to good result in terms of money, time, energy and expectation of not only the learned members of the Bench, but also the Bar as well as the parties to the litigation. It creates a congenial atmosphere where the glory of the judiciary and the Law grows to skyheights. So is the case with regard to the drafting of conveyance/deeds.

Drafting, Pleadings and Conveyance (DPC) is made as a compulsory practical subject forming part of the curriculum of the Law Course in India. It envisages, inter alia, drafting of civil pleadings; criminal complaints and other proceedings; writ petition, appeal-civil, criminal; and also SLP; contempt petition, interlocutory applications, etc. A student who acquires the requisite knowledge, perfection and proficiency in drafting of these matters, shall undoubtedly become a perfect legal professional.

## History of Pleadings

The method of arriving at an issue by alternate allegations has been practised in the civilized countries from earliest times. The art of pleadings apparently is as ancient as any portion of our procedural law. In ancient India it certainly existed but not in the present form. The art of pleading is also traceable in substantially the same form in England in the days of Henry II. The "issue" was found in the first year of the reign of Edward II. It shows that the art of arriving at an issue was not only practised during the reign of Edward II but had been practised even before "for an issue had not been only the constant effect, but the professed aim and the object of pleading". At first the pleadings were oral. The parties actually appeared in person in open Court and oral altercation took place in the presence of the judges. These oral pleading were conducted either by the party himself or by a person who was an eloquent orator and well versed in Dharma Sastras and Koran whom people generally called Pandit and Maulvi in ancient and medieval India respectively. In English countries such person was called narrator and advocates before the adoption of this present lawyers' institution. The Pandits, Maulvis and narrators helped Kings and Judges in the administration of justice in those days.

The duty of the King and the judge was to superindent i.e. to 'moderate' the oral contentions conducted before him. His aim was to arrive at some specific point or matter affirmed on the one side, and denied on the other, and accordingly the parties were said to be 'at issue' and the pleadings were over. The parties, then, were ready to go before a jury if it were at issue. In those days the judges were very strict and they never allowed more than one issue in respect of each cause of action. When a defendant has more than one defence to the plaintiff's claim he had to elect one out of the defences. Since the reign of Queen Victoria the parties were allowed to raise more than a single issue, either of law or fact.

During Viva voce altercation an officer of the court was busy writing on a parchment roll an official report of the allegation of the parties along with the act of Court which together was called record. As the suit proceeded similar entries were made from time to time and on the completion of the proceedings, the roll was preserved as perpetual judicial record. When each pleader in turn started borrowing parchment roll and entered his statement thereon himself, the oral pleading fell into disuse on the obvious defect. Later, with the development of print machinery, paper etc. the method of drawing up the pleading on the plain paper and their interchange between parties started and this happened probably in the reign of Edward IV. The Judicature Act 1873 in England brought in many reforms in the realms of pleading. The modern Indian law of pleading like any other law is based on English system. Civil pleading is governed by the Code of Civil Procedure which lawyer has to master over for the thorough knowledge of practice and procedure required in a civil litigation.

# Meaning of Pleadings 

Pleadings are the statement of facts in writing drawn up and filed in a court by each party to the case stating therein what his contention shall be at the trial and giving all such details as his opponent will need to know in order to prepare his case in answer. In India there are only two pleadings in a suit as defined under Order 6, rule 1 of the Code of Civil Procedure, it says that pleading means "Plaint or Written Statement". This definition is not very clear in itself. The plaint and written statement are defined as:
(a) Plaint: A statement of claims, called the "plaint" in which the plaintiff sets out his cause of action with all necessary particulars; and
(b) Written Statement: A statement of defences, called the "written statement" which the defendant deals with every material fact alleged by the Plaintiff in the plaint and also sets any new facts which tells in his favour, adding such objection as he wishes to take to the claim.

Beside the plaint and the written statement, other pleadings that may be filed, may be divided under two heads: (i) subsequent pleadings, and (ii) additional pleadings.
(i)Subsequent Pleadings: The only subsequent pleading which is filed as a matter of right, without the leave of the court, is a written statement of a plaintiff by way of defence to a plea of set-off set up by a defendant in the written statement of his defences. No other pleading subsequent to the written statement of a defendant other than that by way of defence to a plea of set off can be presented except with the leave of the court and upon such terms as the court may think proper. But the court may at any time require a written statement or an additional written statement from any of the parties and fix a time for presenting the same (O.8, r.9). Any ground of defence which has arisen after the institution of the suit or the presentation of the written statement, may be, raised by the plaintiff or the defendant as the case may be, in his written statement (O.8, r.9). This is also a subsequent pleading. The subsequent pleading, i.e., this written statement in some states is also termed as "replication". This term was formerly used in England where plaintiff's written statement is now called "reply".
(ii) Additional Pleading: Although no pleading subsequent to the written statement of a defendant other than by way of defence to a plea of set-off can be presented without the leave of the court, yet the court may at any time require a written statement or additional written statement from any of the parties, i.e., plaintiff or defendant or both (O.8, r.8). The additional pleadings are not subsequent pleadings in the true sense of the term. They are pleading by way of further and better statement of the nature of the claim or defence or further and better particular of any matter in the pleadings. These pleading may be ordered under order 6, rule 5 of the Code of Civil Procedure.

Under the English Law, pleading has been defined as follows: "pleading includes any petition or summons and also include the statement in writing of the claim or demand of any plaintiff and of the defence of any defendant thereto and of reply of the plaintiff to any counter-claim of a defendant."

# Function and Object of Pleadings 

The object of pleadings is to assist the court and the parties to the dispute in its adjudication. Stable. J., in Pinson v. Lloyds Bank Ltd., (1941) 2 K.B. 72, has expressed the function of pleading in the following words:
"The function of a pleading is not simply for the benefit of the parties and perhaps primarily for the assistance of a Court by defining with precision the area beyond which without the leave of the court, and consequential amendment of pleading, conflict must not be allowed to extend."

The object of pleading is to give a fair notice to each party of what the opponent's case is to; ascertain with precision, the points on which the parties agree and those on which they differ and thus to bring the parties to a definite issue. The purpose of pleading is also eradicating irrelevancy. The parties, thus themselves know what are the matters left in dispute and what facts they have to prove at the trial. They are saved from the expense and trouble of calling evidence which may prove unnecessary in view of the admission of the opposite party. And further, by knowing before hand, what point the opposite party raise at the trial they are prepared to meet them and are not taken by surprise.

Truly speaking the object of the pleading is to narrow down the controversy of the parties to definite issue. The sole object of pleadings is that each side may be fully active to the question that are about to be argued in order that they may have an opportunity of bringing forward such evidence as may be appropriate to the issues. The court has no power to disregard the pleading and reach conclusions that they think are just and proper.

A select committee of eminent lawyers having knowledge of Indian conditions was appointed to frame the present Code of Civil Procedure which has been amended and redrafted in 1976. Order 6, 7 and 8 of the Code of Civil Procedure are very important from the point of view of drafting of pleadings. Appendix A to the Code of Civil Procedure contains some model form of pleadings which are useful.

The pleading should always be drawn up and conducted in such manner so as to evolve some clear and definite issues i.e., some definite propositions of law and/or fact, asserted by one party and denied by the other. But both the parties must agree on the points sought to be adjudicated upon in action. When this has been fairy and properly ascertained then following advantages flow from pleadings:
(i) It is for the benefit of the parties to know exactly what are the matters left in dispute. They may discover that they are fighting about nothing at all; e.g. when a plaintiff in an action of libel finds that the defendant does not assert that the words are true, he is often willing to accept an apology and costs, and so put an end to the action.
(ii) It is also a boon to the parties to know precisely what facts they must prove at the trial; otherwise, they may go through great trouble and expense in procuring evidence of facts which their opponent does not dispute. On the other hand, if they assume that their opponent will not raise such and such a point, they may be taken suddenly by surprise at the trial.
(iii) Moreover, it is necessary to ascertain the nature of the controversy in order to determine the most appropriate mode of trial. It may turn out to be a pure point of law, which should be decided by judge.
(iv) It is desirable to place on record the precise question raised in the action so that the parties or their successor may not fight the same battle over and again.

# Fundamental Rules of Pleadings 

The English law of pleading has got four fundamental rules of pleading upon which Order 6 of the Code of Civil Procedure is based which are set out as under:

1. Every pleading must state facts and not law.
2. It must state all material facts and material facts only.
3. It must state only the facts on which the party's pleading relies and not the evidence by which they are to be proved; and
4. It must state such facts concisely, but with precision and certainty.

## (1) Facts, not law

The first fundamental rule is that neither provisions of law nor conclusions of law should be alleged in a pleading. The pleading should be confined to facts only and it is for the judge to draw such interference from those facts as are permissible under the law of which he is bound to take judicial notice.

# Illustration: 

It will not be sufficient to state that 'Abu Mohammad made a gift of his property' to the plaintiff. The plaintiff should allege here the gift was made, how it was accepted and how possession was delivered; because these are the facts which constitute a valid gift under Muslim Law. To allege that 'Abu Mohammad made a gift' will be a conclusion of law from the facts which are not to be state directly in the pleading.

In a suit for damages for negligence, it is not enough for the plaintiff to state that the defendant has been guilty of negligence' without showing how and in what respect he was negligence and how he became bound to use due care to prevent an injury to other.

When then defendant has to reply to the claim of the plaintiff in a money suit, it is not sufficient for him to state that 'the defendant does not owe to the plaintiff'. But he must allege such fact which goes to prove that in the circumstances the defendant does not owe to the plaintiff. The defendant should state that he never borrowed from the plaintiff, or good were never ordered, or were never delivered, or that they were not equal to the sample.

It is not sufficient in a suit upon a contract for the defendant to, merely, plead the 'the contract is rescinded', the defendant must plead in what manner and by what means he contends that is was rescinded.

The reason for not mentioning the law in the pleading is that it is the duty of the court to find out and examine all plea of Law that may be applicable to the facts of the case. However, the parties can make their submission about law any time. For example, the non maintainability of the suit which is a point of law can be urged although no specific plea has been raised in the pleading. The rule that every pleading must state facts and not law or an interference of law has got following exceptions:
(a) Foreign Laws: The courts do not take any judicial notice of foreign laws and hence they must be pleaded as facts. The status of the foreign country intended to be relied upon should be set-forth as substantially as any other facts. .
(b) Mixed question of Laws and facts: Where a question is one of mixed law and fact, it is permissible and proper to plead both the facts and the legal conclusion. For instance, the defendant may say that the suit is barred by the law of limitation, or he may say he is entitled to set off after narrating the facts on which he bases his conclusions.
(c) Condition precedent: The Code of Civil Procedure provides that any condition precedent the performance of which is intended to be contested shall be distinctly specified in the pleading of the plaintiff or defendant (Order 6 r. 6 of C.P.C.), as for instance, the legality of the notice under section 80, C.P.C.
(d) Custom and Usage of Trades: Custom and usage of any trade and business shall be pleaded like any other facts, if a party wants to rely on them. But a custom repeatedly brought before Court and recognised by them regularly is deemed to have acquired the force of law and need not be pleaded. For example, an occupancy tenant is entitled by local custom and usage to cut trees growing upon his holding it is not necessary for the occupancy tenant to plead this custom, if he wishes to rely on this right to cut the trees. Similarly, a party who wishes to rely on the usage of a particular trade and business and if it is at variance with any provision of the Contract Act, he must not plead the usage of such trade and business with its detailed incident. If it is not pleaded, no evidence to prove it shall be admitted.
(e) The facts of negligence, right or liability, unlawful or wrongful act should be specifically pleaded. Every plea of fact should be specifically raised and proved.

# (2) Material facts 

The second fundamental rule of pleading is that every pleading shall contain only a statement of material facts on which the party pleading relies for his claim or defence. This rule has been enunciated in Order 6, Rule 2 of the Code of Civil Procedure. The omission to observe this rule may increase the difficulty in the Court's task of ascertaining the rights of the parties.

Now, the question arises what are material facts?
The facts which are essential to the plaintiff's cause of action or to the defendant's defence. It can be said that fact is material for the pleading of a party which he is bound to prove at the trial unless admitted by the other party before he can succeed in his claim or defence. If one is in reasonable doubt about a particular fact as a material fact it is better for him to plead that fact rather than omit it because unless a fact is pleaded he shall not be allowed to prove it at the hearing of the suit. A plea of fraud and misrepresentation in a suit must set forth full particulars of fraud and misrepresentation, because these particulars constitute material facts unless raised by the plaintiff or the defendant in his pleading, he will not be allowed to prove at the trial.

Of course, a material fact can be inserted in the pleading by amendment which is the right of the plaintiff and defendant; but when a pleading is amended one is likely to be saddled with the cost of other side. When suit is brought under a particular statute, all facts which are necessary to bring the suit under the statue must be alleged. When a rule of law applicable to a case has an exception to it, all facts are material which tends to take the case out of the rule or out of exception. For instance:
(1) If a childless Mohammedan widow claims one-fourth share in the property of her husband as allowed by Shia law, she must allege that her husband was a Shia.
(2)Where a plaintiff claims an alternative relief, he must plead facts entitling him, for such relief.
(3) Where the question of age or time affects the right of the parties, the facts should be specifically pleaded.
(4) Where a plaintiff sues on the basis of a title he must state the nature of the deed from which he has derived title.
(5) The plea that a woman claiming maintenance has lost her right due to continuous desertion or living in adultery should be specifically raised.
(6) Where the plea is based on custom, it must be stated in the precise form what the custom is. For instance, if a childless Mohammedan widow claims one-fourth share in the property of her husband as allowed by Shia Law, she must allege that her husband was a Shia.

# The following are exception to this fundamental rule of pleading. 

(a) Content of documents: Whenever the contents of document are material, it shall be sufficient in any pleading to state the effect thereof as briefly as possible without setting out whole or any part thereof unless any precise words thereof are material.

Foe instance, if plaintiff's claim is based on a sale-deed, it is sufficient to state that "defendant has sold the property to the property to the plaintiff by a sale-deed dated......"
(b) Matters of Inducement: It means introductory or prefatory facts which should be stated in the first and second paras in the body of the plaint or written statement. Though it is not necessary yet sometimes it is desirable to commence a plaint with some introductory allegations stating who the parties are, what business they carry on how they are related and connected and other surrounding circumstances leading up to the dispute. Though these are not material facts yet these are allowed in England and hence in India too. But the matter of inducement should be reduced to the minimum need.

## (3) Facts, Not Evidence

The third fundamental rule of pleading has been laid down by Order 6, rule 2 of the Code of Civil Procedure. It says that every pleading must contain a statement of material facts but not the evidence by which they are to be proved. The material facts on which a party relies are called Facta Prabanda, i.e. the facts to be proved, and they should be stated in the pleadings. The evidence or facts by which Facta Probanda are to be proved are called Facts Probantia, and they are not to be stated in the pleadings. Facta Probanda are not the facts in issue but only relevant facts which will be proved at the trial in order to established facts in issue. For instance, in a suit of damages for malicious prosecution the plaintiff should only allege in the plaint that the defendant was actuated by malice in prosecuting him. He must not allege that he had previously given evidence against the defendant and the defendant had vowed to take revenge. The plaintiff is by all means entitled to tender evidence to prove this fact. Secondly, in a policy of life insurance, the condition that the policy shall be void, if the holder dies of his own hand, in the defence it is not necessary to state that the assured brought the pistol a few days before his death and made all preparation to kill himself. It is sufficient to state in defence that the assured died of his own hand. In some cases where the facts in issue and relevant facts are so mixed up that it is very difficult to separate them and if it is so the relevant facts may be stated. For example, where custom is based on village administration paper, which is the basis of claim and its sole proof. In such cases the record has to be pleaded.

## (4) Concise Form with Precision and Certainty

The material facts must be stated in a summary form, succinctly and in a strict chronological order. All unnecessary allegations and their details should be omitted in order to attain brevity in pleadings. Pleading is not a place for fine writing but only assertion of hard facts. It is desirable to go straight to the point and state fact, boldly, clearly and concisely and to avoid all paraphrasing and all circumlocutions. As far as possible an active voice should be preferred to passive in pleading. The same person or thing should be called by the same name throughout the pleading. The pleading shall be divided into paragraph numbered consecutively. Dates sums and numbers shall be expressed in figures, even though the pleading should be concise, it should never be obscure. It should be both concise, as well as precise. The parties cannot change the case and get the relief.

A good pleader should bear in mind the following points in relation to a pleading:
i. Describe the names and places accurately and spell them correctly and adopt the same spelling throughout.
ii. One should always avoid the use of pronoun as 'He', 'She', 'This', or 'That'. The plaintiff or the defendant should not be addressed by their names at some place and at some place by the word 'Plaintiff' and ' defendant', call them throughout your pleading by the expression 'the plaintiff' and 'the defendant' as the case may be. Where one has to distinguish between two or more plaintiffs or defendants, they can be referred to as 'the plaintiff Ramashankar' or 'the defendant-Hariharan' as the case may be.
iii. A lawyer should allege all facts boldly and plainly. He should use the language of the document or the act itself; and he should not invent his own language however correct it may be, e.g. of a policy becomes void in case, "the assured shall die of his own hand." Now, inthis case while drafting the pleading instead " the assured killed himself" or he committed suicide," plead that "the assured died of his own hand."
iv. A lawyer should allege all facts boldly and plainly. He should avoid ifs and buts. As far as possible complex sentences should also be avoided. Facts should not be repeated. Pleading should be divided into separate paragraphs and as far as possible only one fact should be contained by one paragraph embodying all necessary particulars in the pleading.
v. Every pleading shall be signed by the party and his advocate and, if the party is unable to sign the pleading it may be signed by this agent.
vi. Every pleading shall be verified by the party or the parties. Verification can also be made by any other person if acquainted with the facts of pleadings. False verification is an offence punishable by the Indian Penal Code.
vii. In cases where a corporation is a party, pleading may be verified by Secretary or by the director or by any other principal officer of that corporation who is able to depose the facts of the case. In verification clause one should denote according to the numbers of paragraph what he verified outy of his own knowledge and what he verified upon the information received and believed to be true.

# Alternative Pleas:

Law does not prohibit a plaintiff from relying on several distinct and different rights in the alternative or a defendant from raising as many distinct and separate defences as he like. For example, a plaintiff may sue for possession of a house belonging to A , as an adopted son of A , and in the alternative under a will executed by A in the plaintiff's favour. A plaintiff may claim proprietary right in a land, or, in the alternative easementary right in an action for preemption the defendant is not prohibited from setting up a plea of estoppels in addition to a plea of denial of custom of pre-emption. A Hindu person claiming under a sale deed from a Hindu widow may support his claim by pleading that the widow separated during the life time of her husband and hence she was the owner of the property which she had sold to him, or in the alternative the widow was in possession for over 12 years and thus became owner by adverse possession.

A defendant in money suit due on promissory note against him may plead that he did not execute the promissory note, and in the alternative the plaintiff claim is barred by the law of limitation. But it must be carefully borne in mind by the draftsman and separately be stated in the pleading. The court will not allow any such pleas on the ground covered by implication unless specifically set out. Thus, in a suit by a son to set aside certain transfers made by his mother on the ground of unsoundness of mind of his mother at the time or the transfer and further averred that the donee was residing with his mother and was completely under his dominion and control and the donee knew the mental condition of the donor.

# SUIT FOR RECOVERY UNDER ORDER XXXVII OF CPC 

## IN THE COURT OF DISTRICT JUDGE (DISTRICT <br> DELHI <br> SUIT NO <br> OF <br> 20.. <br> (SUIT UNDER ORDER XXXVII OF THE CODE OF CIVIL PROCEDURE, 1908)

## IN THE MATTER OF:

M/s ABC Pvt. Ltd.
A Company Incorporated Under the
Companies Act, Having Its Registered Office
At ........, New Delhi.
Through its Director
Shri.....................

PLAINTIFF

VERSUS

M/s XYZ Ltd.
A Company Incprporated Under The
Companies Act. Having Its Registered Office
At ........, Delhi
Through its Director
Shri.....................

...... DEFENDANT

## SUIT FOR RECOVERY OF RS. 4, 19,200/-(Four lakh nineteen thousand two hundred Only) UNDER ORDER XXXVII OF CODE OF CIVIL PROCEDURE, 1908

## MOST RESPECTFULLY SHOWETH:

1. That the Plaintiff is a Company constituted under the Companies Act having its registered office at B-40, Safdarjung Enclave, New Delhi. Mr. P. Executive Director of the Plaintiff is a duly constituted attorney of the Plaintiff and is authorized and competent to sign and verify the plaint, vakalatnama etc. and to institute this suit on behalf of the Plaintiff.
2. That the Plaintiff carries on the business of construction, engineering and designing. The Plaintiff is a builder of international repute and has earned a big name in its business.
3. That the Defendant is a Company incorporated under the Companies Act having their registered office at ......Chandigarh.
4. That the Defendant approached the Plaintiff for construction of a building for their paper mill at Chandigarh some time in the year .....
5. That the plaintiff and the defendant entered into an agreement for the construction of a building a sper the site plan and specifications.
6. That the Plaintiff constructed the building and handed over the possession of the same to the Defendant sometime in......(date).
7. That on $\qquad$ (date), the Plaintiff raised the final bill for Rs. 4,19,200/- on the Defendant on account of the construction of their paper mill at Chandigarh against which the Defendant handed over cheque No. 213456 dated $\qquad$ (date) for Rs. 4,19,200/- drawn on Punjab National Bank, Shahdara, Delhi to the Plaintiff.
8. That the cheque was presented by the Plaintiff, however the same was dishonoured upon presentation vide bank memo dated......
9. That the Plaintiff immediately informed the Defendant about the dishonour of the said cheque and called upon the Defendant to make the payment of the said amount along with interest @ $18 \%$ per annum. However, the Defendant failed to pay the same to the Plaintiff despite repeated requests and reminders.
10. That the Plaintiff therefore finally issued a legal notice dated $\qquad$ (date) to the Defendant calling upon the Defendant to clear the outstanding amount of Rs. 1,39,492/- along with interest at the rate of $18 \%$ per annum w.e.f. $\qquad$ (date) upto the date of payment. However, no payment has been made by the Defendant despite the said notice.
11. That the Defendant is now liable to pay a sum of Rs. 4,19,200/- along with interest @ $18 \%$ per annum from the date on the Plaintiff's bill. The Plaintiff is, claiming interest from......(date) upto the date of filing of this suit @ $18 \%$ per annum.
12. That the cause of action in favour of the Plaintiff and against the Defendant first arose in 2000 when the Plaintiff was approached by the Defendant for construction of their paper mill. It further arose in....... when the said building was completed and handed over to the Defendant and on $\qquad$ when the Plaintiff submitted the final bill for Rs. 4,19,200/- to the Defendant. The cause of action arose on all dates when the Plaintiff called upon the Defendant to make the payment and the later failed to comply with it. The cause of action is still subsisting as the Defendant has failed to pay the outstanding amount despite repeated oral and written requests and reminders from the Plaintiff.
13. The suit is within the period of limitation.
14. This Hon'ble Court has jurisdiction to entertain this suit because the part of the cause of action arose at Delhi. The contract for construction of the paper mill was entered at Delhi, all the payments upto this date have been made at Delhi and the payment of the outstanding amount was also to be made at Delhi. The Administrative Office of the Defendant is situated at Delhi where they carry on the work for their gain.
15. The value of this suit for the purposes of court fee and jurisdiction is Rs. $\qquad$ on which court fee of Rs. $\qquad$ is paid.
16. That this suit is filed under Order XXXVII of the Code of Civil Procedure and no relief has been claimed which does not fall within the ambit of Order XXXVII.
# PRAYER: 

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to :-
(a) Pass a decree for Rs. 4,19,200/-(Four Lakhs Nineteen Thousand and Two Hundred only) with interest @ $18 \%$ per annum from ......(date) upto the date of filing the suit in favour of the Plaintiff and against the Defendant;
(b) award pendentlite and future interest at the rate of $18 \%$ per annum on the above stated amount of Rs. 4,19,200/-(Four Lakhs Nineteen Thousand and Two Hundred only) with interest @ $18 \%$ per annum from .....(date) upto the date of filing the suit in favour of the Plaintiff and against the Defendant;
(c) award cost of the suit in favour of the Plaintiff and against the Defendant; and
(d) pass such other and further order(s) as may be deemed fit and proper on the facts and in the circumstances of this case.

Place:
Date:

Plaintiff
Through
Advocate

## VERIFICATION:

Verified at Delhi on this 1st day of January 20... that the contents of paras 1 to ... of the plaint are true to my knowledge derived from the records of the Plaintiff maintained in the ordinary course of its business, those of paras .... to .... are true on information received and believed to be true and last para is the humble prayer to this Hon'ble Court.

Plaintiff

[NOTE: The above plaint must be supported by an Affidavit]

Note: Mention the correct paragraphs in the verification and also focus on territorial and pecuniary jurisdiction.

# DRAFT AFFIDAVIT 

## IN THE COURT OF DISTRICT JUDGE (DISTRICT <br> $\qquad$ ) DELHI <br> SUIT NO <br> OF <br> 20.. <br> (SUIT UNDER ORDER XXXVII OF THE CODE OF CIVIL PROCEDURE, 1908)

## IN THE MATTER OF:

M/s ABC Pvt. Ltd.
A Company Incorporated Under The
Companies Act, Having Its Registered Office
At New Delhi.
Through its Director
Shri

PLAINTIFF

VERSUS

M/s XYZ Ltd.
A Company Incprporated Under The
Companies Act. Having Its Registered
Office At Delhi
Through its Director
Shri.

DEFENDANT

AFFIDAVIT OF Sh. $\qquad$ S/O. $\qquad$ AGED ABOUT 38 YEARS, R/O. $\qquad$ in the capacity of the director of M/S ABC Pvt. Ltd..

I, $\qquad$ the deponent hereinabove do hereby solemnly affirm and state hereunder:

1. I say that I am the Authorized Representative / Director of the Plaintiff and I am aware of the facts and circumstances of the present suit based upon the records of the Plaintiff maintained in the ordinary course of business and I am duly authorized and competent to swear and file the present suit and affidavit.
2. I say that the accompanying Suit has been drafted and filed by my counsel upon my instructions and contents of the same are true and correct.
3. I say that the documents filed along with plaint are true copies of originals.

DEPONENT
VERIFICATION:
I, $\qquad$ do hereby verify on this $\qquad$ day of January, 2017 at Delhi that the contents of the above said affidavit are true and correct to my knowledge and information and nothing material has been concealed therefrom.

DEPONENT

# SUIT FOR PERMANENT INJUNCTION <br> IN THE COURT OF SENIOR CIVIL JUDGE (DISTRICT <br> SUIT NO. $\qquad$ OF 20.. 

## IN THE MATTER OF:

Sh. Om Veer Singh
S/o. $\qquad$ - ,
R/o. Sainik Nagar, New Delhi

.... PLAINTIFF

VERSUS

1. Dr. U. Basu
S/o $\qquad$ ,
R/o Pragati Vihar Society, Delhi - 92
2. Tapan Kumar,
S/o $\qquad$
R/o Pragati Vihar Society, Delhi - 92

.... DEFENDANTS

## SUIT FOR PERMANENT INJUNCTION

## MOST RESPECTFULLY SHOWETH:

1. That the plaintiff is the permanent resident of the above mentioned address in property bearing no. $\qquad$ Uttam Nagar, New Delhi for the last many year and is living with wife and minor children, as a tenant.
2. That the plaintiff is a tenant in respect of the above said property bearing no $\qquad$ Uttam Nagar, New Delhi consisting two rooms, latrine and kitchen in the above said premises of Rent Rs. $\qquad$ per month excluding electricity and water charges under the tenancy of late Sh $\qquad$ who died on $\qquad$ (date) and late Sh. $\qquad$ used to collect the rent from the plaintiff but late Sh. $\qquad$ did not issued any rent receipt to the plaintiff even after several demands made by the plaintiff but he always used to postpone the issue of rent receipt.
3. That the plaintiff spent a huge amount on the construction of these two rooms in the above said premises at the request of Late Sh. $\qquad$ and Sh. $\qquad$ assured the plaintiff to adjust the said rent (the plaintiff is having the necessary documents/proofs of material for construction of rooms in the above said property). It is also pertinent to mention here that the plaintiff looked after late Sh. $\qquad$ many a times, whenever he fell ill.
4. That at present the plaintiff is having the peaceful possession of premises no. Uttam Nagar, New Delhi and is having the whole necessary documents/record regarding possession (photocopy of Ration Card, School Card is enclosed herewith) but the above said defendants are internded to disturbe the peaceful physical possession of the plaintiff of the above said premises.
5. That the plaintiff is having the whole necessary household goods which are lying/kept in the above said premises and is living peacefully.
6. That the plaintiff has paid the agreed rent @ Rs. ...... per month to late Sh. upto ...... It is also pertinent to mention hare that the legal heirs of late Sh. $\qquad$ are not in the knowledge of the plaintiff and at present also the plaintiff is ready to tender the rent before the legal heirs of late Sh. $\qquad$ .
7. That on $\qquad$ (date) the above said defendant came to the above said premises of the plaintiff and threatened the plaintiff to vacate the tenanted premises immediately otherwise the plaintiff would have to face dire consequences, when the plaintiff asked about their identity then they did not disclose the same, instead started throwing household goods forcibly and illegally and started to quarrel with the plaintiff when the local residents/neighbourers intervened in the matter then the defendants left the spot after threatening for dire consequences and to dispossess the plaintiff forcibly and illegally in the near future with the help of local goondas. The defendants openly stated that the staff of police post $\qquad$ dances at their tune and it is very easy job for them to dispossess any person or to grab the property of any one with the help of the police staff.
8. That immediately on the same date the plaintiff rushed to the police post $\qquad$ to lodge his report against the defendants regarding such incident but duty officer did not lodge the report of the plaintiff. The plaintiff was surprised to see that both the defendants were already present at the Police Post $\qquad$
9. That on $\qquad$ (date), the plaintiff sent a notice to the defendant no. 1 and copy to Chowki Incharge Police Post $\qquad$ by Regd. A.D. (copy of the same is enclosed herewith) but Police Post $\qquad$ staff has not taken any action against the defendants for reasons best known to them.
10. That on $\qquad$ (date), the defendants along with two unknown persons/ whom the plaintiff can recognise by face, came to the above said premises bearing no. $\qquad$ Uttam Nagar, and knocked at the door at odd hours and threatened the plaintiff to come out of the room. The plaintiff saw their faces from gaps of the door and the plaintiff got nervous, and therefore did not come out of two-room apartment. The said persons threatened the plaintiff to vacate the premises immediately. However, then the neighbourers gathered there and they restrained the defendants from dispossessing the plaintiff from the above said premises forcibly and illegally. When the neighbourers threatened them, they left the spot with a threat to come after one or two days with heavy force to dispossess the plaintiff from the above said premises forcibly and illegally.
11. That on $\qquad$ (date), the plaintiff again went to the police post $\qquad$ to lodge the report against the defendants but no Police Officer of police post $\qquad$ is ready to listen against the defendants and they advised the plaintiff to approach to the competent court of law to seek his remedy and to get injunction order against the defendants and the police post $\qquad$
12. That the plaintiff has no other efficatious remedy except to approach to this Hon'ble court for seeking relief of injunction against the defendants from interfering in the peaceful possession of the premises no. $\qquad$ Uttam Nagar, New Delhi.
13. That the cause of action arose on different date when the defendants threatened the plaintiff to vacate the premises no. $\qquad$ Uttam Nagar, New Delhi and threatened the plaintiff of dire consequences and further to dispossess him from the above premises bearing no. $\qquad$ Uttam Nagar, New Delhi forcibly and illegally. The cause of action lastly arose on $\qquad$ when the defendants again threatened and tried to dispossess the plaintiff from the premises no. $\qquad$ Uttam Nagar, New Delhi forcibly and illegally with the connivance of the Local Police. The cause of action still subsists as the threat of the defendants to dispossess the plaintiff and to create disturbance in the peaceful possession of the premises no. $\qquad$ Uttam Nagar, New Delhi continues.
14. The value of this suit for the purposes of court fee and jurisdiction is Rs. $\qquad$ on which court fee of Rs. $\qquad$ is paid.
15. This Hon'ble Court has jurisdiction to entertain this suit because the part of the cause of action arose at Delhi and the suit property is situated within the territorial jurisdiction of this Hon'ble Court.

# PRAYER: 

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to:
(a) pass the decree for Permanent Injunction in favour of the plaintiff and against the defendants thereby restraining the defendants, their representatives, employees, agents etc. from dispossessing the plaintiff forcibly and illegally from the tenanted premises bearing no. Uttam Nagar, New Delhi and also from interfering in the peaceful possession of the above said premises.
(b) award cost of the suit in favour of the Plaintiff and against the Defendants;
(c) pass such other and further order(s) as may be deemed fit and proper on the facts and in the circumstances of this case.

Place:
Date:

Plaintiff
Through
Advocate

## VERIFICATION:

Verified at Delhi on this .....of January 20... that the contents of paras 1 to .. of the plaint are true to my knowledge derived from the records of the Plaintiff maintained in the ordinary course of its business, those of paras .. to $\ldots$ are true on information received and believed to be true and last para is the humble prayer to this Hon'ble Court.

Plaintiff

[NOTE: This plaint has to be supported by an affidavit]


# APPLICATION FOR TEMPORARY INJUNCTION <br> IN THE COURT OF SENIOR CIVIL JUDGE (DISTRICT <br> $\qquad$ ), DELHI 

IA NO. $\qquad$ OF 20...
$\qquad$ $\frac{\text { IN }}{\text { SUIT NO. }}$ $\qquad$ OF 20...

## IN THE MATTER OF:

Sh. Om Veer Singh,
S/o $\qquad$
$\mathrm{R} / \mathrm{o} \ldots$ $\qquad$ PLAINTIFF/APPLICANT VERSUS

1. Dr. U. Basu, S/o $\qquad$
$\mathrm{R} / \mathrm{o} \ldots$.
2. Sh. Tapan Kumar, S/o $\qquad$
$\mathrm{R} / \mathrm{O} \ldots$ DEFENDANTS/RESPONDENTS

## APPLICATION FOR TEMPORARY INJUNCTION UNDER ORDER XXXIX, RULE 1 \& 2 READ WITH SECTION 151 OF THE CODE OF CIVIL PROCEDURE, 1908

## MOST RESPECTFULLY SHOWETH:

1. That the plaintiff has filed a suit for permanent injunction which is pending for disposal before this Hon'ble Court.
2. That the contents of the accompanying suit for permanent injunction may kindly be read as a part and parcel of this application which are not repeated here for the sake of brevity.
3. That the plaintiff/applicant has got a prima-facie case in his favour and there is likelihood of success in the present case.
4. That in case the defendants are not restrained by means of ad-interim injunction for dispossessing the plaintiff from the above said premises no. $\qquad$ Uttam Nagar, New Delhi and from interfering in physical peaceful possession of the above said premises, the plaintiff shall suffer irrepairable loss and injury and the suit shall become anfractuous and would lead to multiplicity of the cases.
5. That the balance of convenience lies in favour of the plaintiff and against the defendants.

## PRAYER:

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to :-a) Pass ex-parte ad interim injunction restraining the defendants, their associates, servants, agents and their representatives from interfering into the peaceful physical possession of the plaintiff in the above said premises and from dispossessing the applicant/plaintiff from the same.
b) pass such other and further order(s) as may be deemed fit and proper on the facts and in the circumstances of this case.

Place:
Date:

Plaintiff /Applicant
Through
Advocate

[NOTE: This Application has to be supported by an affidavit].


# APPLICATION UNDER ORDER XXXIX RULE 2-A 

IN THE COURT OF SH. $\qquad$ SENIOR CIVIL JUDGE (DISTRICT $\qquad$ ), DELHI

IA NO. $\qquad$ OF 20..
IN
SUIT NO. $\qquad$ OF 20..

IN THE MATTER OF:

ABC

...PLAINTIFF/APPLICANT

Versus

XYZ

...DEFENDANT/RESPONDENT

## APPLICATION UNDER ORDER XXXIX RULE 2-A READ WITH SECTION 151 OF THE CODE OF CIVIL PROCEDURE, 1908 ON BEHALF OF THE PLAINTIFF

## MOST RESPECTFULLY SHOWETH:

1. That the above noted suit for injunction is pending before this Hon'ble Court and the contents of the plaint be read as part of this application. The plaintiff/applicant is tenant in suit premises bearing House No..................., Uttam Nagar, New Delhi and the defendant is landlord of the same.
2. That on an application U/O 39, R $1 \& 2$ for interim stay against interference in peaceful possession of the plaintiff/applicant as well as dispossession from the said premises, without due process of law was filed by the plaintiff/applicant against the defendant/respondent alongwith the plaint.
3. That on........(date) this Hon'ble Court was pleased to grant interim injunction in favour of the plaintiff/applicant and against the defendant/respondent for not to interfere in the peaceful possession of the plaintiff/applicant and not to dispossess him without due process of law from the suit property.
4. That on dt. $\qquad$ the defendant/respondent inspite of the service and knowledge of the above interim injunction orders dt $\qquad$ took forcible possession of the suit premises with the help of anti social elements in utter disregard of the orders of this Hon'ble Court and the applicant/plaintiff's household goods were thrown on the roadside.
5. That the defendant/respondent has thus knowingly and willfully disobeyed and violated the injunction orders issued by this Hon'ble Court on $\qquad$ (date) and he is as such guilty of disobedience of the orders of this Hon'ble Court and has rendered himself liable to be detained in civil imprisonment and attachment of his property. List of properties is attached.

# PRAYER: 

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to:
a) take appropriate action U/O 39 R 2-A of the Code of Civil Procedure and other provisions of law may be taken against the defendant/respondent and his property may be directed to be attached and he may be directed to be kept in civil imprisonment for the maximum term.
b) direct restoration of the possession of the suit property to the plaintiff/applicant.
c) any other appropriate orders/directions may also be passed as may be deemed fit in the facts and circumstances of the case in favour of plaintiff/applicant.

Delhi.
Dated:

Plaintiff/Applicant
Through
Advocate

(Note: An affidavit, duly attested by oath commissioner, in support of this application is to be attached with to this application)


# APPLICATION TO SUE AS AN INDIGENT PERSON <br> IN THE COURT OF..........., ROHINI COURT (DIST......), DELHI SUIT NO.......OF....... 

## IN THE MATTER OF :

X $\qquad$
S/o $\qquad$
R/o $\qquad$ , New Delhi

...APPLICANT/PLAINTIFF
Versus
Y $\qquad$
S/o $\qquad$
R/o $\qquad$ , New Delhi

...RESPONDENT/DEFENDANT

## APPLICATION UNDER ORDER XXXIII READ WITH SECTION 151 OF THE CODE OF CIVIL PROCEDURE, 1908

## MOST RESPECTFULLY SHOWETH:

1. That the applicant has filed the above titled suit which is pending disposal before this Hon'ble Court.
2. That the contents of the accompanying suit may kindly be read as a part and parcel of this application which are not repeated here for the sake of brevity.
3. That the applicant is an indigent person and has no movable or immovable property and has no source of income. Therefore is unable to pay the requisite amount of court fee stamp as required by law.
4. That the applicant undertakes to pay the entire court fee if the case is decreed in his favour.
5. That there are sufficient reasons for the acceptance of the present application and for granting permission to the applicant to institute the present suit as an indigent person.

## PRAYER:

It is therefore most respectfully prayed that the Hon'ble Court may:
a. allowed to sue as an indigent person in the interest of justice.
b. to pass such further orders/directions as it may deem fit and proper.

Date:
Place:

Applicant
Through
Advocate

[Note: The petition must be supported by an affidavit].


# SUIT FOR EJECTMENT AND DAMAGES 

## BEFORE THE SENIOR CIVIL JUDGE (DISTRICT <br> $\qquad$ ), DELHI SUIT NO. $\qquad$ OF 20..

## IN THE MATTER OF,

Mrs. Surjit Kaur Sahi W/O
Mr. Avinder Singh Sahi S/O
Both R/o $\qquad$ Chandigarh

...PLAINTIFFS
VERSUS
Power Grid Corporation of India Ltd.
Hemkunt Chamber, Nehru Place, New Delhi-110029
Through its Chairman/Managing Director

...DEFENDANT

## SUIT FOR EJECTMENT AND DAMAGES FOR WRONGFUL USE AND OCCUPATION

## MOST RESPECTFULLY SHOWETH:

1. The plaintiff being the owners of flat no. $\qquad$ Nehru Place, New Delhi let out the said flat to M/s. National Power Transmission Corporation Limited (a Government of India undertaking) now called as Power Grid Corporation of India Limited, having their registered office at Hemkunt Chamber, Nehru Place, New Delhi-110 019 for a period of three years with effect from ......(date) vide unregistered Lease deed (copy annexed as Annexure 'A'). The delivery of the possesson of the said premises was simultaneous on the said date.
2. That the period of three years referred above starting from $\qquad$ expired on $\qquad$ That after the expiry of the said Lease the defendant became a month to month tenant of the plaintiffs.
3. That the plaintiffs being in need of the premises in question approached the defendant for vacation of the same on various dates (give dates). However, the defendant who were approached through their officers did not agree to the plaintiff's demand. The plaintiffs thereafter served a legal notice through their Counsel, Shri $\qquad$ (copy annexed as Annexure 'B') under section 106 of Transfer of Property Act terminating the said tenancy on mid-night of.......(date)
4. That the defendant received the plaintiff's legal notice U/s. 106 of the Transfer of property Act on .....(date) i.e. clear 15 days before the last day of ......(date) and thus is a valid notice under the Transfer of Property Act (proof of the service of legal notice is annexed to same as Annexure 'B')
5. That however, the defendant even after receiving the said legal notice have neither vacated the premises nor shown their intention to vacate. Thus the defendant from ......(date) are in wrongful use and occupation @ Rs. 1,000/- per day as the rate of rent in the area are for such premises prevailing and the plaintiffs have rightly assessed the rate of Rs. 1,000/- per day. The same rate was demanded in the legal notice dated...... That since the premises were needed by the plaintiffs for their own purposes they will have to take on rent the premises of same size in the same area where the flat is situated and the plaintiffs have done a market survey during the search for the flat and found that the rate of rent in the area is Rs. 100/- to Rs. 150/- per sq. feet. The plaintiffs own flat which is 370 sq. ft. super area will be available in the market for Rs. 37000/- to 55,500/- per month. The plaintiffs does not have means to take on rent a flat for own purposes at such high rates and thus needed the flat and for this reason asked the defendant to vacate the premises.
6. The defendant is presently paying a monthly rent of Rs. 6808/- per month (Rupees six thousand eight hundred eight) for the plaintiffs flat measuring 370 sq. ft. super area. The plaintiffs premises are not governed by the Delhi Rent Control Act as the rate of rent is more than Rs. 3,500/- and thus the Hon'ble Court has jurisdiction to try the matter.
7. The cause of action in the present case arose on $\qquad$ when the plaintiffs approached the defendant for the vacation of the said flat. The cause of action further arose on $\qquad$ when the plaintiffs again approached the officers of the defendant for the vacation of the flat who however did not oblige. The cause of action further arose when the plaintiffs served a legal notice dated ...... through their advocate Shri Ajit Panday asking the defendant to vacate the same by ....... The said notice was duly received on ...... However, the defendant did not vacate the flat in question. The cause of action in the present case is a continuing one.
8. That since the property whose possession is sought is situated in Delhi. The Lease for the premises was executed in Delhi and delivery of possession made in Delhi. And since the premises are not covered by Delhi Rent Control Act. The Hon'ble Court has jurisdiction to try the matter.
9. That the court fee payable has been calculated advalorem as per the chart/section 7 of the Court Fee Act on the annual rent received by the plaintiffs. The annual rent is Rs. arrived at by multiplying monthly rent of Rs............. by 12. On this a court fee of Rs. $\qquad$ is paid. The plaintiffs undertake to pay any additional court fee that may be found due by the Hon'ble court.

# PRAYER: 

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to:
(i) pass a decree for ejectment against the defendant and in favour of plaintiffs ;
(ii) pass a decree for payment of damages @ Rs. 1,000/- per day for wrongful use and occupation of the flat by the defendant ;
(iii) Any other relief deemed fit and proper may also be given.
(iv) Costs of the case may also be given.

Delhi

Dated

PLAINTIFFS
THROUGH
ADVOCATE

# VERIFICATION : 

Verified at Delhi on ... day..... of , 20... that the contents of paras 1 to .... are true to our personal knowledge and those of paras ... to .... are true \& correct on the basis of legal advice received and belived to be true. Last para is prayer to the Hon'ble Court.

PLAINTIFFS

[NOTE : This plaint has to be supported by an affidavit]


# SUIT FOR SPECIFIC PERFORMANCE OF CONTRACT <br> IN THE COURT OF <br> ROHINI COURT (DIST......), DELHI <br> SUIT NO. <br> OF......... 

## IN THE MATTER OF :

X $\qquad$
S/o $\qquad$
R/o $\qquad$ , New Delhi

...PLAINTIFF
Versus
Y $\qquad$
S/o $\qquad$
R/o $\qquad$ , New Delhi

...DEFENDANT

## SUIT FOR SPECIFIC PERFORMANCE OF CONTRACT

## MOST RESPECTFULLY SHOWETH:

1. That the plaintiff is a resident of $\qquad$
2. That the defendant is the absolute owner of the property bearing no.......admeasuring (give details of the property) (hereinafter refered to as the suit property).
3. That the plaintiff was in need of the property for residential purpose and came to know that the Defendant is interested in selling the suit property.
4. That the plaintiff approached the defendant for purchasing the suit property on.....(date) and the plaintiff and the defendant discussed the terms and conditions.
5. That on....(date), the plaintiff and the defendant entered into an agreement in writing whereby the defendant agreed to sell his property to the plaintiff for Rs........... The copy of the agreement is annexed as Annexure A.
6. That the plaintiff paid Rs.........to the defendant as earnest money and it was decided that the balance of Rs........will be paid on....... and the sale deed will be executed on the possession of the suit property will be handed over to the plaintiff on the payment of the balance amount.
7. That on......(date), the plaintiff approached the defendant and requested him to execute the sale deed along with handing over of the possession of the suit property to the plaintiff. However, the defendant refused to execute the sale deed.
8. That the plaintiff approached the defendant for execution of the sale deed on various occasions (mention the dates), however, the defendant refused to execute the sale deed on one pretext or the other.
9. That the plaintiff finally issued a legal notice dated.....(date) to the defendant calling upon the defendant to perform his part of the agreement by executing the sale deed and handing over the possession of the suit property to the plaintiff. However, the defendant failed to comply with his part of the agreement and did not reply to the legal notice.
10. That the plaintiff is ready and willing to perform his part of agreement by paying the balance amount.
11. That the cause of action arose on.....(date) when the defendant agreed to sell the suit property to the plaintiff. The cause of action further arose on............. It further arose......That the cause of action is still subsisting as the defendant has refused to perform his part of the agreement.
12. That the suit is within the period of limitation.
13. That this Hon'ble Court has jurisdiction to entertain this suit because the cause of action arose within the territorial jurisdiction of the court.
14. That the requisite court fees have been paid.

# PRAYER: 

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to:
a. pass a decree of specific performance of the agreement in favour of the plaintiff and against the defendant directing the defendant to execute the sale deed and hand over the possession of the suit property to the plaintiff,
b. award cost of the suit in favour of the plaintiff and against the defendant; and
c. pass such other and further order(s) as may be deemed fit and proper on the facts and in the circumstances of this case.

Place:
Date:

Plaintiff
Through
Advocate

## VERIFICATION:

Verified at Delhi on this 1st day of January 20... that the contents of paras 1 to ... of the plaint are true to my knowledge derived from the records of the Plaintiff maintained in the ordinary course of its business, those of paras .... to 14 are true on information received and believed to be true and last para is the humble prayer to this Hon'ble Court.

Plaintiff

[NOTE: The above plaint must be supported by an Affidavit]


# MODEL DRAFT FOR WRITTEN STATEMENT <br> IN THE COURT OF SHRI <br> CIVIL JUDGE <br> (DISTRICT <br> $\qquad$ ), DELHI <br> SUIT NO. OF <br> 2017 

X $\qquad$ ... PLAINTIFF
VERSUS
Y $\qquad$ ...DEFENDANT

## WRITTEN STATEMENT ON BEHALF OF THE DEFENDANT

## MOST RESPECTFULLY SHOWETH:

## PRELIMINARY ObJECTIONS:

1. That the suit is barred by limitation under Article $\qquad$ of the Limitation Act and is liable to be dismissed on this ground alone.
2. That this Hon'ble Court has no jurisdiction to entertain and try this suit because. $\qquad$
3. That the suit has not been properly valued for the purpose of court fees and jurisdiction and is therefore liable to rejected outrightly.
4. That there is absolutely no cause of action in favour of the Plaintiff and agianst the Defendant. The suit is therefore liable to be rejected on this ground also.
5. That the suit is bad for non-joinder of necessary parties, namely $\qquad$
6. That the suit is bad for mis-joinder of Z.
7. That the suit is barred by the decree dated $\qquad$ passed in suit No. $\qquad$ titled Y Versus X by Sh. $\qquad$ Sub-Judge, Delhi, The present suit is therefore barred by the principle of res-judicata and therefore liable to be dismissed on this short ground alone.
8. That the suit is liable to be stayed as a previously instituted suit between the parties bearing No. $\qquad$ is pending in the Court of Sh. $\qquad$ Sub-Judge, Delhi
9. That the suit has not been properly verified in accordance with law.
10. That the Plaintiff's suit for permanent injunction is barred by Section 41 (h) of the Specific Relief Act since a more efficacious remedy is available to the Plaintiff. The Plaintiff has alleged breach of contract by the Defendant. Assuming, though not admitting, that the Defendant has committed any alleged breach, the remedy available to the Plaintiff is by way of the suit for specific performance.
11. That the Plaintiff's suit for permanent injunction is also barred by Section 41 (i) of the Specific Relief Act because he has not approached this Hon'ble Court with clean hands and his conduct has been most unfair, dishonest and tainted with illegality.
12. That the Plaintiff's suit for declaration is barred by Section 34 of the Special Relief Act as the plaintiff has omitted to claim further consequential relief available to him.
13. That the suit is barred by Section 14 of the Specific Relief Act as the contract of personal service cannot be enforced.
14. That the suit is liable to be dismissed outrightly as the Plaintiff has not given the mandatory notice under Section 80 of the Code of Civil Procedure/Section 14 (1) (a) Rent Control Act/Section 478 of the Delhi Municipal Corporation Act.
15. That the suit is liable to be dismissed as the Plaintiff firm is not registered under Section 69 of the Indian Partnership Act and as such is not competent to institute this suit.
16. That the present suit is barred by Section 4 of the Benami Transaction (Prohibition) Act, 1988, and is therefore liable to be dismissed outrightly.

# ON MERITS : 

Without prejudice to the preliminary objections stated above, the reply on merits, which is without prejudice to one another, is as under:-

1. That the contents of para 1 of the plaint is correct and is admitted.
2. That the contents of para 2 of the plaint are denied for want of knowledge. The Plaintiff be put to the strict proof of each and every allegation made in the para under reply.
3. That the contents of para 3 of the plaint are absolutely incorrect and are denied. It is specifically denied that the Plaintiff is the owner of the suit property. As a matter of fact, Mr. N is the owner of the suit property.
4. That with respect to para 4 of the plaint, it is correct that the Defendant is in possession of the suit property. However, the remaining contents of para under reply are absolutely incorrect and are denied. It is specifically denied that
5-10. (Each and every allegation must be replied specifically depending upon the facts of each case. The above reply on merits is therefore only illustrative in nature.)
5. That para 11 of the plaint is incorrect and is denied. There is no cause of action in favour of the Plaintiff and against the Defendant because The plaintiff is therefore liable to be rejected outrightly.
6. That the contents of para 21 is not admitted. This Hon'ble Court has no jurisdiction to entertain this suit because the subject matter of this suit exceeds the pecuniary jurisdiction of this Hon'ble Court.
7. The the contents of para 13 is not admitted. The suit has not been properly valued for the purpose of court fee and jurisdiction. According to the Defendant the correct valuation of the suit is Rs.

## PRAYER:

It is, therefore most respectfully prayed that this Hon'ble Court may be pleased to:
a) Dismiss the suit of the plaintiff.
b) Award costs to the defendant.
c) Pass any other just and equitable order as deemed fit in the interest of justice.

Delhi 
Dated

DEFENDANT
THROUGH
ADVOCATE

## VERIFICATION :

Verified at Delhi on ... day..... of , $20 \ldots$ that the contents of paras 1 to .... Of the preliminary objection and para...to... of reply on merits are true to my personal knowledge and those of paras ... to ....of preliminary objection and para...to... of reply on merits are true \& correct on the basis of legal advice received and belived to be true. Last para is prayer to the Hon'ble Court.

DEFENDANT

[NOTE: Counter Claim, Set off can be joined in the Written Statement and the same may be verified and supported by affidavit]


# CAVEAT UNDER SECTION 148-A OF CPC <br> IN THE HIGH COURT OF DELHI AT NEW DELHI CAVEAT NO. /2017 <br> (ARISING OUT OF THE JUDGMENT AND ORDER DATED <br> IN SUIT NO. <br> TITLED AS ABC v. XYZ PASSED BY SH. <br> , CIVIL JUDGE, <br> DISTRICT, DELHI) 

In the matter of:
XYZ
S/o
R/o

...Petitioner

Versus

ABC
S/o
R/o

...Respondent/Caveator

## CAVEAT UNDER SECTION 148-A OF THE CODE OF CIVIL PROCEDURE, 1908 BY RESPONDENT/CAVEATOR.

Most Respectfully Showeth:

1. That Sh. $\qquad$ Civil Judge, $\qquad$ District, Delhi has passed order against appellants in Civil Suit No. $\qquad$ titled as ABC v. XYZ on
$\qquad$ whereby application for amendment U/O VI Rule 17 CPC filed by plaintiff/would be petitioner, was dismissed.
2. That the caveator is expecting that the plaintiff/would-be petitioner may file a Civil Misc. (Main) Petition under Article 227 of Constitution of India against said order in this Hon'ble Court as such this caveat is being filed.
3. That the caveator has a right to appear and contest the Civil Misc. (Main) Petition if preferred by the plaintiff/would-be petitioner.
4. That the caveator desires that he may be given the notice of the filing of the Civil Misc. (Main) Petition as and when the same is filed by the plaintiff/would-be petitioner, to enable caveator to appear at the time of hearing for admission and no stay may be granted without hearing the caveator/respondent.
5. That a copy of this caveat has been sent by Regd. A/D post to the plaintiff/would be Petitioner.

## PRAYER:

It is, therefore, most respectfully prayed that nothing may be done in Civil Misc. that may be filed by the petitioner without notice to the caveator or his counsel.

Delhi
Dated:

Caveator
Through
Advocate

(Note: An affidavit of the caveator, duly attested by oath commissioner, in support of this application is to be attached with to this application.)


# TRANSFER PETITION UNDER SECTION 25 OF CPC 

Sec 25 of CPC 1908 states that on an application made by a party and after notice to the parties and after hearing them the Supreme Court may at any stage if satsfied that such a order is needed in the interest of justice may under this section order that any suit, appeal or any other proceeding be transferred from a High Court or other civil court in one state to High Court or other civil court in another state.

## IN THE SUPREME COURT OF INDIA ORIGINAL CIVIL JURISDICTION <br> TRANSFER PETITION (CIVIL) NO. $\qquad$ OF 2017 <br> (UNDER SECTION 25 OF THE CODE OF CIVIL PROCEDURE, READ WITH ORDER XLI, SUPREME COURT RULES, 2013.)

IN THE MATTER OF:
J $\qquad$ S/o $\qquad$ R/O $\qquad$ 

...PETITIONER

VERSUS

1. Union of India, Through its Secretary, Ministry of Defence, South Block,New Delhi-110001
2. Chief of Air Staff, Vayu Bhawan, New Delhi-110001.
3. Air Officer Commanding -in-Chief
Western Air Command,
Subrato Park, New Delhi-110010
4. Group Captan A $\qquad$
Station Commander, Air Force
Station Suratgarh.
5. Presiding Officer

Court Martial, Subrato Park,New Delhi. 

...RESPONDENTS

## AND IN THE MATTER OF:

TRANSFER OF CIVIL WRIT PETITION NO.727/2015 FILED BY THE PETITIONER AGAINST THE RESPONDENTS PENDING IN THE HIGH COURT OF DELHI AT NEW DELHI, TO THE HIGH COURT OF JUDICATURE AT ALLAHABAD.
To
The Hon'ble Chief Justice of India,
And his Companion Justices of the Hon'ble Supreme Court of India at New Delhi

# MOST RESPECTFULLY SHOWETH: 

1. That the petitioner is seeking Transfer of Civil Writ Petition No.727/2015 filed by the Petitioner against the respondents pending in the High Court of Delhi at New Delhi, to the High Court of Judicature of Allahabad, titled "JWO BP Misra Versus Union of India \& Ors."

## 2. BRIEF FACTS:

i. The Petitioner joined as Airmen in the Trade Flight Mechanic Air Frame and later after conversion course became Air Frame Fitter after passing the necessary examination and training. During the period petitioner also gained a promotion to the rank of Corporal, Sergeant and later Junior Warrant Officer - Class-II, a Gazetted post. The Petitioner was also awarded three good conduct badge Pay each after 4 year of Services for very good character and good proficiency in his trade. There was no whisper of any kind of misconduct while working at various places during 22 year of service as per the directions of the Respondents. The same is a matter of record and speaks in volumes about the Character and Trade proficiency of the petitioner.
ii. The Petitioner got his last rank after passing due examination and consideration of last Annual Confidential Report (ACRS) Significantly in the year 1998 the Petitioner was awarded in assessment $94 / 100$ as exceptional which speaks about the high caliber of the Petitioner in his trade.
iii. The Petitioner was compelled to file a Redress of Grievances ROG against Respondent No. 6 for non grant of leave and unwanted harassment in many ways i.e. sending on temporary duty assigning Secondary Duties, not granting of leave and denial of even monthly salary for four months which is a matter of record. The Petitioner has one son suffering with asthmatic problem and came on posting to present place as per the Medical advice of the authorities.
iv. The Petitioner was charge sheeted and later the same was dropped as he has complained about the grievances against his Squadron Technical Officer (STO) for illegal harassment.
v. The petitioner has all the apprehensions of his life as such filed a FIR at the Police Station for seeking protection from the officials of the Respondents. The Security Officer of the Respondents gave undertaking before the Police on behalf of Respondents that no harm will be done to the Petitioner. After withdrawing the Complaint by the Petitioner, the Petitioner was immediately sent on temporary duty to Nalia in Gujarat due to irritation of complaint. The Petitioner had no alternative but to proceed as directed without being his turn. The harassment of the Petitioner continued at the behest of the Respondent No. 6 Commanding Officer C.O. and his Subordinates. After strong and heavy earth quake in whole of the Gujarat in the morning the Petitioner was directed to go back to his Unit knowing fully well of non-availability of transport which was totally abandoned due to the earth quake, the same is matter of record. However the Petitioner has to beg for his food and somehow reached his unit to avoid wrath of the Respondents by way of disciplinary action for misconduct of not disobedience.
vi. The Petitioner aggrieved by such highhandedness of the Respondents filed an Appeal under 26 of Air Force Act for redressal of his grievances. The Petitioner gave a reminder for disposal of his appeal under Section 26 of the Air Force Act. The Appeal was rejected without speaking order with stereo type of order devoid of merits. The Petitioner filed application for permission to file Civil Case and for grant of leave. The same was not granted by the Respondents and even denied the acknowledgment of the receipt. Application for extension of service was rejected and ordered to be discharged. The Petitioner was orally threatened to abstain from raising such applications.
vii. The Petitioner was put under Close arrest without informing his family as even directed by the Hon'ble Supreme Court in D.K. Basu's case, which curtails the liberty of the Petitioner in a illegal manner. The reasons are yet to be known. The Petitioner sought interview with the Station Commander which was granted later on 9.10.2001. The Station Commander instead of redressing of the grievance and consoling the Petitioner for his illegal close arrest, further threatened the Petitioner with a dire consequence and of further putting him under close arrest and threatened for Court Martial.
viii. The Petitioners Summary of Evidence $2^{\text {nd }}$ is completed in an illegal manner without providing him a copy of the previous Summary of Evidence which is mandatory to meet the requirements of principles of Natural Justice. The petitioner is now informed that he is likely to Court martialled by way of GCM. and since last 4 months the Petitioner is under constant threat of disciplinary action at the hands of the Respondents for no fault of his where as all officials under the Respondents have joined hands together to harass the Petitioner by all means and make example case for others. The Petitioners extension application is also rejected as the last Respondent has spoiled his ACR for the year 2003 and 2005 without any communication to the Petitioner or in a Counseling to the Petitioner as provided under the provisions of the Air Force Act. Hence Writ Petition No. 727 of 2015 filed for initiation of appropriate enquiry and disciplinary action against the officials for illegal harassment of the Petitioner and for quashing of the ACRs 2003 \& 2005 and subsequent order of discharge.
ix. Respondents decided to conduct General Court Martial in retaliation to certain observations and queries by this Hon'ble Court to explain the reason of close arrest in September, 2014. That no legal aid or defence Advocate was provided. All members were ignorant about law and worked at the tune of the Judge Advocate and all pleas of petitioner were disallowed in arbitrary manner. Preliminary objections were not taken by General Court Martial on record. The Petitioner approached Hon'ble High Court of Delhi by way of Civil Misc. Application in which notice was issued. General Court Martial without adhering to law and provisions and principles of natural justice passed the order, "to be reduced to the rank of Cpl. From JWO (JCO) subject to confirmation." The copy of the order was not given to the Petitioner to deprive him to approach this Hon'ble Court. The Petitioner was released form open arrest which speaks in volumes about the high-handedness of the Respondents to deprive him of any legal aid or counseling by any one. Proceeding copy of General Court Martial were denied to the Petitioner by which denied the statutory right of Appeal u/s 161 (1) of Air Force Act. Even affidavit of defence witness was not taken on record.
x. The Petitioner was discharged. Pension stopped. Regular threat to life is given as numerous incidents of elimination of Airmen who raise voice against commissioned officers. The Petitioner is in bad financial state and has no money to meet his day to day expenses. The petitioner has no means to incur heavy expenditure in travelling to Delhi for conduct of his case. The petitioner also feels that his life will be put to an end by the respondents. Fearing safety of his life the petitioner has moved his family bag and baggage to District Pratap Garh (U.P.). That the High Court of judicature at Allahabad are near to the place of residence of the petitioner and the petitioner feels that the writ Petition No. 727 of 2015 titled B.P. Mishra V/s U.O.I. be transferred to the High Court of Judicature at Allahabad as the petitioner has no trust and faith in the respondent and they can stoop to any level and the petitioner fears for his life. Hence the petitioner is seeking transfer of his case to the High Court at Allahabad.
3. This Transfer Petition is being filed by the Petitioner for transferring the Civil Writ Petition No.727/2015 filed by the Petitioner at the High Court of Delhi at New Delhi on amongst others the following grounds.

# GROUNDS 

I. Because the Petitioners have no trust and faith in the respondents as they are prejudiced and using influence and every other illegal method to defeat the petitioner. Thus the petitioner is seeking the transfer of the case from the High Court of Delhi at New Delhi to High Court of Judicature at Allahabad.
II. Because the petitioner have no trust and faith in Opposite party as they had in past acted with malice and making life threatening attempts and petitioner fears for his and of his family's life.
III. Because the petitioner is discharged from service and is not getting Pension and dues and petitioner is reduced in state of penury and is not in a position to conduct case in Delhi.
IV. Because on 31.5.2015 the Petitioner was discharged. His pension stopped and he received regular threat to life is given as numerous incidents of elimination of Airmen who raise voice against commissioned officers.
V. Because the Petitioner is in bad financial state and has no money to meet his day to day expenses. The petitioner has no means to incur heavy expenditure in travelling to Delhi for conduct of his case. The petitioner also feels that his life will be put to an end by the respondents. Fearing safety of his life the petitioner has moved his family bag and baggage to District Pratapgarh (U.P.). That the High Court of judicature at Allahabad are near to the place of residence of the petitioner and the petitioner feels that the writ Petition No. 727 of 2015 titled B.P. Mishra V/s U.O.I. be transferred to the High Court of Judicature at Allahabad as the petitioner has no trust and faith in the respondent and they can stoop to any level and the petitioner fears for his life.
VI. Because in the facts and circumstances stated above, it would be in the interest of justice that the said Civil Writ Petition No. 727/2015 filed by the petitioner against the respondents pending in the High court of Delhi at New Delhi be transferred to High Court of Judicature at Allahabad (U.P.). Even otherwise there is no likelihood of disposal of writ petition No. 727/2015 due to heavy back log of cases. The copy of the civil writ petition No. 727 / 2015 is Annexure P-1.
4. That the petitioner has not filed any other similar transfer petition before this Hon'ble Court so far in respect of this matter.

# PRAYER: 

In view of the above facts and circumstances, it is respectfully submitted that this Hon'ble Court may be pleased:
a) To pass order for transfer of the Civil Writ Petition No. 727/2015 filed by the Petitioner against the respondent titled "JWO BP Mishra Vs. Union of India" from High Court Delhi at New Delhi to the High Court of Judicature at Allahabad.
b) Any other and further order as may be deemed fit and proper may also be passed.

FILED BY:

DATE OF DRAWN $\qquad$
DATE OF FILING
NEW DELHI

ADVOCATE FOR THE PETITIONER

[NOTE: To be supported by an affidavit]


# EXECUTION APPLICATION <br> IN THE COURT OF <br> EXECUTION PETITION NO. $\qquad$ OF 2017 <br> IN <br> CIVIL SUIT NO. $\qquad$ OF 2015 

A

... DECREE HOLDER

Versus

B

...JUDGMENT DEBTOR

THE DECREE HOLDER PRAYS FOR EXECUTION OF THE DECREE/ORDER DATED DD/MM/YYYY, THE PARTICULARS WHEREOF ARE STATED IN THE COLUMNS HEREUNDER:-

Police Station:-

| 1. | No. of Suit |  |
| :-- | :-- | :-- |
| 2. | Name of Parties |  |
| 3. | Date of Decree/order of which <br> execution is sought |  |
| 4. | Whether an appeal was filed against <br> the decree / order under execution |  |
| 5. | Whether any payment has been <br> received towards satisfaction of decree- <br> order |  |
| 6. | Whether any application was made <br> previous to this and if so their dates <br> and results |  |
| 7. | Amount of suit along with interest as <br> per decree or any other relief granted <br> by the decree |  |
| 8. | Amount of costs if allowed by Court |  |
| 9. | Against whom execution is sought |  |
| 10 | In what manner court's assistance is <br> sought |  |

## PRAYER:

The Decree Holder prays that the execution of the decree passed in the case may be granted.

Place:
Date:

Decree Holder
Through
Advocate of Decree Holder

# VERIFICATION: 

Verified on.....at......that the contents of this application are true to my knowledge or belief.

DecreeHolder

Note: Fill in the details in the table above as per the facts of the case.

* The application for execution shall be accompanied by a duly certified copy of the decree or order, or by the Original, or by the Minutes of decree or order until the decree or order is drawn up. Judge may allow execution before sealing of decree order.


# PETITIONS UNDER THE HINDU MARRIAGE ACT, 1955 

Before giving any model form of application under the matrimonial laws, it is necessary to know what kind of petitions are contemplated in matrimonial causes. The Hindu Marriage Act, 1955, has provided for the following important petition:
1.Petition for restitution of conjugal rights (sec. 9)
2.Petition for judicial separation (sec. 10)
3.Petition for void or nullity of marriage (sec. 11)
4.Petition for divorce by dissolution of marriage (sec. 13)
5.Petition for maintenance pendent lite (sec.24)
6.Petition for alimony and maintenance (sec. 25)
7.Petition for custody of children (sec.26)

Such reliefs are also obtained under the Special Marriage Act, 1954, the Indian Divorce Act, 1889, and other personal laws.
Under the rules farmed by the Bombay High Court it is necessary to state the following facts in the petition for (i) judicial separation, (ii) Nullity of marriage, and (iii) Divorce in addition to the point given in O. VII, r. 1, C.P.C. and S. 20(1) of the Hindu Marriage Act. (i) Place and date of marriage, (ii) name of the state of domicile of the wife and husband before and after marriage (iii) the principal permanent address where there is any cohabited including the address where they raised together, (iv) birth or ages of such issues, (v) whether there had been any proceeding in India, if so what wre they and with what result, and on behalf of whom? (vi) Matrimonial offences or offence charged should be set out in separate paragraphs with time and place of its commission, (vii) property presented at or about the time of marriage and jointly owned by both husband and wife, and (viii)relief or reliefs prayed for. All matrimonial petitions shall lie in the Court of the District Judge (Family Courts wherever established) within whose local limits of the jurisdiction the marriage was solemnised, or within whose local limit of the jurisdiction the parties to the marriage last resided together, or within whose jurisdiction the respondent has been residing; but in the Metropolis of Mumbai, Calcutta, Chennai and Ahmadabad, these petition shall lie in the City Civil Court of the respective metropolitan town.

By virtue of Section 14 Hindu Marriage Act, 1955, the Petition for Divorce cannot be presented with in one year of marriage unless leave is taken from the court to present before on the ground of exceptional hardship.
The Petitions under Hindu Marriage act are to be presented before District Judge within the local limits of whose jurisdiction
(a) The Marriage was solemnized; or
(b) The respondent at the time of presentation of the petition, resides, or
(c) The parties to the marriage last resided together, or
(d) In case the wife is the petioner, where she is residing on the date of presentation of the petition, or
(e) The petioner is residing at the time of presentation of the petition in a case where the respondent is, at the time, residing outside the territories to which th Act extends, or has not been heard of as being alive for a period of seven years or more by those persons who would naturally have heard of him if he were alive.

The districts in which the Family Courts have been established under Family Courts Act, 1984, the petitions shall lie before the Principal Judge, Family Court ( Section 7 and 8 Family Courts Act, 1984)
Every petition shall state distinctly the following facts-
(a) That the marriage of the petioner was solemnized with the respondent in accordance with Hindu rites and ceremonies on ....at.....and and affidavit to the effect has to be enclosed
(b) That there is no collusion between the petitioner and the other party in presenting the petiotion for annulment of the marriage. This fact need not be pleaded in case of petition under section 11 of the Act.
(c) In case the Petion for Divorce is filed on the ground of cruelty of the respondent, it has to be specificaaly pleaded that the petioner has not condoned the act of the respondent.
(d) Where the petition for divorce on mutual consent is filed, affidavits of both the parties are to be attached.
(e) In case of petition for Restitution of Conjugal rights, it has to be pleaded that the respondent has withdrawn from the company of petitioner without any reasonable cause.
(f) In the petition under the Act, the details regarding the status and place of residence of the parties to the marriage before the marriage and at the time of presentation of the petition have to be provided.


# PETITION FOR RESTITUTION OF CONJUGAL RIGHTS 

## IN THE COURT OF PRINCIPAL JUDGE, FAMILY COURT (DISTT..), DELHI

## HMA PETITION NO. OF 2017

IN THE MATTER OF :
X
s/o
R/o

... PETITIONER

VERSUS

Y
w/o
R/o

...RESPONDENT

## PETITION FOR RESTITUTION OF CONJUGAL RIGHTS UNDER SECTION 9 OF THE HINDU MARRIAGE ACT, 1955

Most Respectfully Showeth:

1. That a marriage was solemnized between the parties according to Hindu rites and ceremonies on (date) at........(place). The said marriage is registered with the Registrar of marriage. A certified copy of the relevant extract from the Hindu Marriage Register......... is filed herewith. An affidavit, duly attested declaring and affirming these facts is also attached.
2. That the status and place of residence of the parties to the marriage before the marriage and at the time of filing the petition are as follows:

|  | Husband <br> Status | Age Place of Residence | Status | Wife <br> Age Place of Residence |
| :--: | :--: | :--: | :--: | :--: |

(i) Before marriage
(ii) At the time of
filing the petition
(Whether a party is a Hindu by religion or not is as part of his or her status).
3. That the (In this paragraph state the names of the children, if any, of the marriage together with their sex, dates of birth or ages).
4. That the respondent has, without reasonable excuse, withdrawn from the society of the petitioner with effect from.............(The circumstances under which the respondent withdrew from the society of the petitioner be stated in few paragrahs depending upon the facts).
5. That the petition is not presented in collusion with the respondent.
6. That there has not been any unnecessary or improper delay in filing the petition.
7. That there is no other legal ground why relief should not be granted.
8. That there have not been any previous proceedings with regard to the marriage by or on behalf of any party.

Or

There have been the following previous proceedings with regard to the marriage by or on behalf of the parties:

| Serial | Name of <br> Parties | Nature of <br> Proceedings with <br> Section of that Act | Number <br> and year of <br> the case | Name and <br> location <br> of court | Result |
| :-- | :-- | :-- | :-- | :-- | :-- |

(i)
(ii)
(iii)
(Choose whichever is applicable to the facts)
9. That the marriage was solemnized at............... The parties last resided together at........... The parties are now residing at..................(Within the local limit of the ordinary original jurisdiction of this Court.)
10. That this Hon'ble Court has jurisdiction to try and entertain this petition.

# PRAYER: 

In view of the above facts and circumstances, it is, therefore, most respectfully and humbly prayed that this Hon'ble Court may be pleased to grant a decree of restitution of conjugal rights under Section 9 of the Hindu Marriage Act in favour of the petitioner.
Any other relief/order/Direction this Hon'ble Court may deem fit in the interest of justice and equity.

Place: Delhi
Date:

PETITIONER
Through
ADVOCATE

## VERIFICATION:

The above named petitioner states on solemn affirmation that paras 1 to of the petition are true to the petitioner's knowledge and paras..................to.................. are true to the petitioner's information received and believed to be true by him/her.

Verified at..................................(Place)
Dated.....................

PETITIONER

[NOTE: AN AFFIDAVIT OF PETITIONER IS TO BE APPENDED]


# PETITION FOR JUDICIAL SEPARATION <br> IN THE COURT OF PRINCIPAL JUDGE, FAMILY COURT (DISTT..), DELHI HMA PETITION NO. $\qquad$ OF 2017 

IN THE MATTER OF :
X
s/o
R/o
$\qquad$ PETITIONER
VERSUS
Y $\qquad$
w/o
R/o $\qquad$ RESPONDENT

## PETITION FOR JUDICIAL SEPARATION UNDER SECTION 10 OF THE HINDU MARRIAGE ACT, 1955

Most Respectfully Showeth:

1. That the marriage was solemnized between the parties according to Hindu rites and ceremonies on $\qquad$ (date) at $\qquad$ (place). The said marriage is registered with the Registrar of marriage. A certified copy of the relevant extract from the Hindu Marriage Register $\qquad$ is filed herewith.
2. That the status and place of residence of the parties to the marriage before the marriage and at the time of filing the petition are as follows:

|  | Husband <br> Status | Place of <br> Residence | Status | Wife <br> Age | Place of <br> Residence |
| :--: | :--: | :--: | :--: | :--: | :--: |

(i) Before marriage
(ii) At the time of
filling the petition
(Whether a party is a Hindu by religion or not is as part of his or her status).
3. That the (In this paragraph state the names of the children, if any, of the marriage together with their sex, dates of birth or ages).
4. That the respondent has. $\qquad$ (any one or more of the grounds available under section 10 may be pleaded here. The matrimonial offences charged should be set in separate paragraphs with times and places of their alleged commission. The facts on which the claim to relief is founded should be stated in accordance with the Rules and as distinctly as the nature of the case permits.)
5. (where the ground of petition is on the ground specified in clause (i) of section 13 (1). The petitioner has not in any manner been necessary to or connived at or condoned the acts complained of.
6. (Where the ground of petition is cruelty). The petitioner has not in any manner condoned the cruelty.
7. That the petition is not presented in collusion with the respondent.
8. That there has not been any unnecessary or improper delay in filing the petition.
9. That there is no other legal ground why relief should not be granted.
10. That there have not been any previous proceedings with regard to the marriage by or on behalf of any party.

Or

There have been the following previous proceedings with regard to the marriage by or on behalf of the parties:

| Serial | Name of <br> Parties | Nature of <br> Proceedings with <br> Section of that Act | Number <br> and year of <br> the case | Name and <br> location <br> of court | Result |
| :-- | :-- | :-- | :-- | :-- | :-- |

(i)
(ii)
(iii)
(iv)
(Choose whichever is applicable to the facts)
11. That the marriage was solemnized at............... The parties last resided together at........... The parties are now residing at.................... (Within the local limit of the ordinary original jurisdiction of this Court)
12. That this Hon'ble Court has jurisdiction to try and entertain this petition

# PRAYER: 

In view of the above facts and circumstances, it is, therefore, most respectfully and humbly prayed that this Hon'ble Court may be pleased to grant a decree of Judicial Separation under Section 10 of the Hindu Marriage Act in favor of the petitioner.
Any other relief/order/Direction this Hon'ble Court may deem fit in the intrest of justice and equity.

Place: Delhi
Date:

PETITIONER
Through
ADVOCATE

## VERIFICATION:

The above named petitioner states on solemn affirmation that paras 1 to $\qquad$ of the petition are true to the petitioner's knowledge and paras $\qquad$ to $\qquad$ are true to the petitioner's information received and believed to be true by him/her.
Verified at $\qquad$ (Place)
Dated $\qquad$

PETITIONER

Note: An affidavits of petitioner is to be appended.


# PETITION FOR DISSOLUTION OF MARRIAGE BY A DECREE OF DIVORCE 

## IN THE COURT OF PRINCIPAL JUDGE, FAMILY COURT (DISTT..), DELHI <br> HMA PETITION NO. $\qquad$ OF 2017

IN THE MATTER OF:
X $\qquad$
S/O
R/O

... PETITIONER

VERSUS

Y $\qquad$
W/O
R/O

...RESPONDENT

## PETITION FOR DISSOLUTION OF MARRIAGE BY A DECREE OF DIVORCE UNDER SECTION 13 OF THE HINDU MARRIAGE ACT, 1955

Most Respectfully Showeth:

1. That the marriage was solemnized between the parties according to Hindu rites and ceremonies after the commencement of the Hindu Marriage Act on $\qquad$ at
$\qquad$ The said marriage is registered with the Registrar of marriage. A certified copy of the relevant extract from the Hindu Marriage Register..............is filed herewith.
2. That the status and place of residence of the parties to the marriage before the marriage and at the time of filing the petition are as follows:

|  | Husband <br> State | Place of <br> Residence | Status | Wife <br> Age | Place of <br> Residence |
| :-- | :-- | :-- | :-- | :-- | :-- |

(i) Before marriage
(ii) At the time of filing the petition
(Whether a party is a Hindu by religion or not is as part of his or her status).
3. (In this paragraph state the names of the children, if any, of the marriage together with their sex, dates of birth or ages).
4. That the respondent......(one or more of the grounds specified in section 13 may be pleaded here. The facts on which the claim to relief is founded should be stated in accordance with the Rules and as distinctly as the nature of the case permits. If ground as specified in clause (i) of Section 13 (i) is pleaded, the petitioner should give particulars as nearly as he can, of facts of voluntary sexual intercourse alleged to have been committed. The matrimonial offences/offences charged should be set is separate paragraphs with the time and places of their alleged commission.)
5. (Where the ground of petition is on the ground specified in clause (i) of sub-section (1) of Section 13. The petitioner has not in any manner been accessary to or connived at or condoned the acts(s) complained of).
6. (Where the ground of petition is cruelty). The petitioner has not in any manner condoned the cruelty.
7. That the petition is not presented in collusion with the respondent.
8. That there has not been any unnecessary or improper delay in filing the petition.
9. That there is not other legal ground why relief should not be granted.
10. That there have not been any previous proceedings with regard to the marriage by or on behalf of any part.
Or
There have been the following previous proceedings with regard to the marriage by or on behalf of the parties:

| Serial | Name of | Nature of | Number | Name Result |
| :--: | :--: | :--: | :--: | :--: |
| Parties | Proceedings with Section of that Act | and year of the case | and location of court |  |

(i)
(ii)
(iii)
(iv)
(Choose whichever is applicable to the facts)
11. That the marriage was solemnized at................. The parties last resided together at........... The parties are now residing at..................... (Within the local limits of the ordinary original jurisdiction of this Court.)
12. That this Hon'ble Court has jurisdiction to try and entertain this petition

# PRAYER: 

In view of the above facts and circumstances, it is, therefore, most respectfully and humbly prayed that this Hon'ble Court may be pleased to grant a decree of divorce under Section 13 of HMA in favor of petitioner.
Any other relief/order/Direction this Hon'ble Court may deem fit in the intrest of justice and equity.

PETITIONER
THROUGH
ADVOCATE

## VERIFICATION:

The above named petitioner states on solemn affirmation that paras 1 to $\qquad$ of the petition are true to the petitioner's knowledge and paras $\qquad$ to $\qquad$ are true to the petitioner's information received and believed to be true by him/her.
Verified at $\qquad$ (Place)
Dated $\qquad$

PETITIONER

[Note: An affidavit of the petitioner is to be appended.]


# PETITION FOR DISSOLUTION OF MARRIAGE BY A DECREE OF DIVORCE BY MUTUAL CONSENT 

## IN THE COURT OF PRINCIPAL JUDGE, FAMILY COURT (DISTT..), DELHI

## HMA PETITION NO. $\qquad$ OF 2017

IN THE MATTER OF:
X $\qquad$ ... PETITIONER NO. 1
AND
Y $\qquad$ ... PETITIONER NO. 2

## PETITION FOR DISSOLUTION OF MARRIAGE BY A DECREE OF DIVORCE BY MUTUAL CONSENT UNDER SECTION 13-B(1) OF THE HINDU MARRIAGE ACT, 1955

Most Respectfully Showeth:

1. That a marriage was solemnized between the parties according to Hindu rites and ceremonies on $\qquad$ (date) at $\qquad$ (place). A certified copy of the relevant extract from the Hindu Marriage Register is filed herewith. An affidavit, duly attested statting these facts is filed herewith.
2. That the status and place of residence of the parties to the marriage before the marriage and at the time of filing the petition are as follows:

|  | Husband |  |  | Wife |  |
| :-- | :--: | :--: | :--: | :--: | :--: |
|  | Status | Age | Place of <br> Residence | Status | Age |

(i) Before marriage
(ii) At the time of
filing the petition
(Whether a party is a Hindu by religion or not is as part of his or her status).
3. (In this paragraph state the place where the parties to the marriage last resided together and the names of the children, if any, of the marriage together with their sex, dates of birth or ages.)
4. That the parties to the petition have been living separately since $\qquad$ and have not been able to live together since then. (In few paragraphs, mention the reasons for not being able to live together. In case there is a settlement between parties, the same can also be mentioned).
5. That the parties to the petition have mutually agreed that their marriage should be dissolved.
6. That the mutual consent has not been obtained by force, fraud or undue influence.
7. That the petition is not presented in collusion.
8. That there has not been any unnecessary or improper delay in instituting the proceedings.
9. That there is no other legal ground why relief should not be granted.
10. That the petitioners submit that this Court has jurisdiction to entertain this petition. (Mention how the court has jurisdiction to entertain the petition).

# PRAYER: 

In view of the above facts and circumstances, it is, therefore, most respectfully and humbly prayed that this Hon'ble Court may be pleased to grant a decree of divorce on mutal consent thereby dissolving the marriage between petitioner No. 1 and Petitioner oNo. 2 on the ground of mutual consent.

PETITIONER NO. 1
PETITIONER NO. 2
THROUGH
COUNSEL

## VERIFICATION:

The above named petitioner states on solemn affirmation that paras 1 to $\qquad$ of the petition are true to the petitioner's knowledge and paras $\qquad$ to $\qquad$ are true to the petitioner's information received and believed to be true by him/her.
Verified at $\qquad$ (Place)
Dated $\qquad$

PETITIONER NO. 1
PETITIONER NO. 2

[Note: Separate affidavits of petitioner no. 1 and petitioner no. 2 to be appended]


# DRAFT AFFIDAVIT IN MATRIMONIAL PLEADINGS 

## IN THE COURT OF PRINCIPAL JUDGE, FAMILY COURT, ROHINI COURT (DIST.....), DELHI. <br> H.M.A. PETITION NO. /2015

IN RE:-
SMT. A
W/O
R/O

...PETITIONER

VERSUS

SH. B
W/O
R/O

...RESPONDENT

## AFFIDAVIT OF SMT. A, W/O...., D/O...... AGED ABOUT........., R/O................

I, the above named Deponent do hereby solemnly affirm and declare as under:

1. That I am the petitioner in the aforesaid matter and as such I am well aware about the facts of the present case and thus competent to depose the same.
2. That my marriage was solemnized with the respondent, according to Hindu Rites and ceremonies on $\qquad$ at Delhi.
3. That the present petition has not been presented in collusion with the respondent.
4. That there is no improper or undue delay in filing the present petition.
5. That the consent for filing the present petition has not been obtained by fraud, force, pressure or undue influence.
6. That the contents of the accompanying petition U/S $\qquad$ of the Hindu Marriage Act. 1955, as amended upto date, have been drafted by my counsel as per my instructions and contents of the same have been duly read and understood by me and after fully understanding the contents of the same, I hereby state that the fact stated therein are all true and correct to my knowledge and the fact stated therein may kindly be read as part and parcel of the present affidavit also as the contents of the same have not been reproduced herein for the sake of brevity.

## DEPONENT

VERIFICATION:
I, $\qquad$ do hereby verify on this $\qquad$ day of January, 2016 at Delhi that the contents of the above said affidavit are true and correct to my knowledge and information and nothing material has been concealed therefrom.

## DEPONENT


# APPLICATIONS UNDER THE INDIAN SUCCESSION ACT <br> PETITION FOR GRANT OF PROBATE 

## IN THE HIGH COURT OF DELHI AT NEW DELHI (TESTAMENTARY \& INTESTATE JURISDICTION)

PROBATE CASE NO. OF 2017

IN THE MATTER OF:
THE ESTATE OF LATE SH.........(DECEASED)
IN THE MATTER OF:
X $\qquad$
S/O
R/O

... APPLICANT/PETITIONER

VERSUS

1. State of $\qquad$
2. Y $\qquad$
S/O
R/O

...RESPONDENTS

## PETITION FOR GRANT OF PROBATE

To
The Hon'ble Mr Justice..................., Chief Justice
And his Companion Justices of this Hon'ble Court
Most Respectfully Showeth:

1. That the present petition is filed by the petitioner for the grant of probate in respect of the estate of deceased Late $\mathrm{Sh} . \ldots \ldots . . \mathrm{S} / \mathrm{O} \ldots .$. At the time of his death on.........the deceased was residing
2. That during his lifetime before his death the deceased had bequeathed his estate in the manner specified in his last and final testament/will dated....., which was made by him in the sound state of mind. The Original Will is annexed as Annexure A.
3. That the said will was duly made by the deceased in presence of the witnesses whose names, addressed and signatures appear at the end of the Will.
4. That by virtue of the said will, the deceased has bequeathed......(mention how the deceased has bequeathed his estate, name, relation and the individual share of the person and also mention whether he has excluded any of his legal heirs from the will.).
5. That a description of the relatives of the deceased, and their respective residences are given below:
(1) Son (Petitioner)
(2) Brother, Sri.............resident of
(3) Widow, Sreemati............resident of
(4) Mother, Sreemati.............resident of
(5) Daughter, Sreemati..........resident of
(All the relatives will be made as Respondents)
6. That the amount of the assets of the deceased which are likely to come to the hands of the petitioner, are detailed in Schedule-A, which is annexed with the present petition. The petitioner has set forth all the assets and liabilities with complete particulars of the estate of the deceased as the petitioner could ascertain as of now with the best of his efforts.
7. That so far as your petitioner has been able to ascertain and is aware there are no properties and effects other than those specified in the affidavit of assets.
8. That the petitioner undertakes in case of any other properties and effects coming to his hands to pay Court-fees payable in respect thereof.
9. That there is no legal impediment to the grant of probate in favour of the petitioner.
10. That the petitioner undertakes to execute the Will of the testator as per his wishes and undertake to take all steps as per his wishes and desires and directions of the deceased as contained in the Will annexed.
11. That the petitioner is claiming the probate of the Will and has filed this petition being the named executor in the Will.
12. That to the best of the belief of the petitioner, no petition has been made to any other court for the purpose of the said Will.
13. That the deceased died and had a fixed abode within the territorial jurisdiction of this Hon'ble Court. The immovable property is also situated within the jurisdiction of this Hon'ble Court and therefore this Hon'ble Court has the jurisdiction to entertain, try and decide this petition.

# PRAYER: 

It is, therefore, most humbly prayed that:
a. The probate of the Will be granted to the petitioner.
b. Any other or further relief which this Hon'ble Court may deem fit just proper and necessary may also be granted in favour of the petitioner.

Place:
Date:

PETITIONER
THROUGH
ADVOCATE 

## VERIFICATION:

I, $\qquad$ S/o $\qquad$ R/o. $\qquad$ the petitioner in the above petition, declare that what is stated herein is true to the best of my information and belief. Last para is the prayer to this Hon'ble Court.

Verified at New Delhi on this $\qquad$ day of $\qquad$

PETITIONER

## VERIFICATION:

I, $\qquad$ S/o. $\qquad$ R/o. $\qquad$ one of the witness to the last WILL and Testament of the Testator mentioned in the above petition, declare that I was present and saw the said Testator affix his signature on the WILL annexed to the above petition and acknowledge the writing annexed to the above petition to be his Last WILL and Testament in my presence.

WITNESS NO. 1

## VERIFICATION:

I, $\qquad$ W/o. $\qquad$ R/o. $\qquad$ one of the witness to the last WILL and Testament of the Testator mentioned in the above petition, declare that I was present and saw the said Testator affix his signature on the WILL annexed to the above petition and acknowledge the writing annexed to the above petition to be his Last WILL and Testament in my presence.

WITNESS NO. 2

[NOTE : To be supported by an affidavit]


# PETITION FOR GRANT OF LETTERS OF ADMINISTRATION 

## IN THE COURT OF THE DISTRICT JUDGE (DISTRICT <br> $\qquad$ ), DELHI <br> CASE NO. <br> UNDER ACT XXXIX OF 1925

## IN THE MATTER OF A PETITION FOR LETTERS OF ADMINISTRATION OF THE ESTATE OF THE LATE

$\qquad$
IN THE MATTER OF:
X $\qquad$ ...PETITIONER

VERSUS

1. STATE $\qquad$
2. Y $\qquad$ ..RESPONDENTS

## PETITION FOR GRANT OF LETTERS OF ADMINISTRATION

Most Respectfully Showeth:

1. That the present petition is filed by the petitioner for the grant of letters of administration in respect of the estate of deceased Late $\mathrm{Sh} . \ldots \ldots . . . \mathrm{S} / \mathrm{O} \ldots .$. At the time of his death on. $\qquad$ the deceased was residing. $\qquad$
2. That during his lifetime before his death the deceased had bequeathed his estate in the manner specified in his last and final testament/will dated....., which was made by him in the sound state of mind. The Original Will is annexed as Annexure A.
3. That the said will was duly made by the deceased in presence of the witnesses whose names, addressed and signatures appear at the end of the Will.
4. That by virtue of the said will, the deceased has bequeathed......(mention how the deceased has bequeathed his estate, name, relation and the individual share of the person and also mention whether he has excluded any of his legal heirs from the will.).
5. That a description of the relatives of the deceased, and their respective residences are given below:
(1) Son (Petitioner)
(2) Brother, Sri.............resident of
(3) Widow, Sreemati............resident of
(4) Mother, Sreemati.............resident of
(5) Daughter, Sreemati..........resident of
(All the relatives will be made as Respondents)
6. That the amount of the assets of the deceased which are likely to come to the hands of the petitioner, are detailed in Schedule-A, which is annexed with the present petition. The petitioner has set forth all the assets and liabilities with complete particulars of the estate of the deceased as the petitioner could ascertain as of now with the best of his efforts.
7. That so far as your petitioner has been able to ascertain and is aware there are no properties and effects other than those specified in the affidavit of assets.
8. That the petitioner undertakes in case of any other properties and effects coming to his hands to pay Court-fees payable in respect thereof.
9. That there is no legal impediment to the grant of letters of administration in favour of the petitioner.
10. That the petitioner undertakes to execute the Will of the testator as per his wishes and undertake to take all steps as per his wishes and desires and directions of the deceased as contained in the Will annexed.
11. That the petitioner is claiming the letters of administration of the Will and has filed this petition being the beneficiary mentioned in the Will.
12. That to the best of the belief of the petitioner, no petition has been made to any other court for the purpose of the said Will.
13. That the deceased died and had a fixed abode within the territorial jurisdiction of this Hon'ble Court. The immovable property is also situated within the jurisdiction of this Hon'ble Court and therefore this Hon'ble Court has the jurisdiction to entertain, try and decide this petition.

# PRAYER: 

It is, therefore, most humbly prayed that:
a. The Letters of Administration of the Will be granted to the petitioner.
b. Any other or further relief which this Hon'ble Court may deem fit just proper and necessary may also be granted in favour of the petitioner.

Place:
Date:

PETITIONER
THROUGH
ADVOCATE

## VERIFICATION:

I, $\qquad$ S/o. $\qquad$ R/o. $\qquad$ the petitioner in the above petition, declare that what is stated herein is true to the best of my information and belief. Last para is the prayer to this Hon'ble Court.

Verified at New Delhi on this $\qquad$ day of $\qquad$

PETITIONER

## VERIFICATION:

I, $\qquad$ S/o $\qquad$ R/o $\qquad$ one of the witness to the last WILL and Testament of the Testator mentioned in the above petition, declare that I was present and saw the said Testator affix his signature on the WILL annexed to the above petition and acknowledge the writing annexed to the above petition to be his Last WILL and Testament in my presence.

WITNESS NO. 1

# VERIFICATION: 

I, $\qquad$ W/o $\qquad$ R/o $\qquad$ one of the witness to the last WILL and Testament of the Testator mentioned in the above petition, declare that I was present and saw the said Testator affix his signature on the WILL annexed to the above petition and acknowledge the writing annexed to the above petition to be his Last WILL and Testament in my presence.

WITNESS NO. 2

[NOTE : To be supported by an affidavit]


# PETITION FOR THE GRANT OF SUCCESSION CERTIFICATE 

## IN THE COURT OF THE ADMINISTRATIVE CIVIL JUDGE, ROHINI COURT (DIST.....), DELHI SUCCESSION PETITION NO.........OF..........

IN THE MATTER OF:
X $\qquad$
S/O
R/O

... APPLICANT/PETITIONER

VERSUS

1. STATE $\qquad$
2. Y $\qquad$
S/O
R/O

...RESPONDENTS

## PETITION FOR THE GRANT OF SUCCESSION CERTIFICATE IN RESPECT OF THE GOODS, DEBTS AND SECURITIES ETC. OF <br> (deceased) UNDER SEC. 372 OF THE INDIAN SUCCESSION ACT, 1925.

## MOST RESPECTFULLY SHOWETH:

(1) That the above-named $\qquad$ died at ....(residential address)..... on or about the $\qquad$ day of $\qquad$ 20 $\qquad$
(2) That the said Deceased died intestate and that due and diligent search has been made for a Will but none has been found.
(3) That deceased named above hereinafter referred to being the said deceased who had been during his lifetime till his death permanently residing and living at the abovesaid premises within the jurisdiction of this court and was by nationality and faith a Hindu citizen of India ruled by Dayabhaga /Tamil School of Hindu Law.
(4) That the said Deceased at the time of his death left him surviving his only next-of-kin according to $\qquad$ law (state law) residing at. $\qquad$
(5) That the Petitioner as $\qquad$ (state relation) of the Deceased claims to be entitled to a share of the estate.
(6) That there is no impediment under Section 370 of the Indian Succession Act, 1925 or under any other provision of this Act or any other enactment to the grant of the certificate or the validity thereof, if it were granted.
(7) That the Petitioner has truly set forth in Schedule I hereto the securities in respect of which the certificate is applied for. The Succession Certificate is required for purpose of $\qquad$ (state the purpose for which succession certificate is required). The said assets in respect of which the Succession Certificate is required are under the value of Rs. $\qquad$
(8) That no application has been made to any District Court or Delegate or to any High Court for Probate of any Will of the said Deceased or for letters of Administration with or without the Will annexed to his property and credits.
(9) That no application for Succession Certificate in respect of and debt or security belonging to the estate of the Deceased has been $\qquad$ (Or if made, state to what Court, by what person and what proceedings have been taken) made to any District Court or Delegate or to any High Court.
(10) That ad valorem duty of Rs. payable relating to grant of Succession Certificate hereunder prayed for has been paid.
(11) That this application is made bonafide.

# PRAYER: 

The Petitioner therefore prays:
(i) That a Succession Certificate, may be granted to the Petitioner in respect of debts and securities set forth in Schedule I hereto with power to collect and/or receive and/or realise the same inclusive of all interests accrued thereon and to sell and/or negotiate and/or deal with the same without any impediment.
(ii) That the Petitioner be exempted from presenting any security on that account.

PETITIONER
THROUGH
COUNSEL

## VERIFICATION:

I the Petitioner above named, do solemnly declare that what is stated in paragraphs ............ is true to my knowledge and that what is stated in the remaining paragraphs is true to information received from $\qquad$ and believed to be true.

PETITIONER

[NOTE: To be supported by an affidavit]


# PETITIONS UNDER CONSTITUTIONAL LAW 

## WRITS

## Meaning and evolution of the concept of Writs:

The term 'writ petition' in its general connotation means a Petition filed before the competent Courts, having prerogative powers, when some special and inherited rights of the people are infringed bu the government or its officials.
in the common laws of English this term is well settled as a 'prerogative writ' which means a writ special associated with then king. It resembled the extraordinary authority of the Crown/ Court. In English prerogative writs were issued only at the suit of the king but later on it was made available to the subject also.

## Habeas Corpus

Habeas Corpus is a writ requiring the body of a person to be brought before a judge or Court. In other words, it is prerogative process for securing the liberty of the subject which affords an effective means of immediate reLease form unlawful unjustifiable detention whether in prison or in private custody. It is an ancient supreme right of the subject. Its object is the vindication of the right of the personal liberty of the subject. The High Courts and The Supreme Court have got a very wide power of protecting the liberty of subjects, under Art. 226 and Art. 32 respectively of the Constitution. These powers are to be exercised on certain fixed judicial principles and not in an arbitrary manner. The jurisdiction can be exercised if the Court is satisfied that the detention is illegal or improper, where the Court can also embark upon an inquiry as to whether the enactment under which a person is detained is proper or not. A proceeding of habeas corpus is essential of a civil character, and is concerned with the personal liberty of a citizen. However, the power is exercised on the criminal side of the High Court's appellate jurisdiction. The High Courts and the Supreme Court exercise this power when satisfied that the matter is of urgency, and no other legal remedy is available.
An application for habeas corpus may be made by any person interested in the liberty of the detenue without unreasonable delay; and it must be supported by an affidavit of the petitioner. Ordinarily a rule nisi (to show cause) is issued by the Court in the first instance. It is not open to Court to go behind the reasons given by Government for the detention, and it must see the motive of the impugned law and the bonafide of the Government. If the impugned detention has been induced by malafide and some other strenuous reasons and not for bonafide cause, it shall be quashed and the individual shall be set at liberty.

## Mandamus

It is high prerogative writ of a most extensive remedial nature. The Supreme Court and high court have power respectively under Article 32 and Article 226 of the Indian constitution to issue this writ in the form of a command directing any person holding public office under the government or, statutory bodies or, corporation or, to an inferior Court exercising judicial or quasi-judicial function to do a particular act pertaining to his office or duty and which the court issuing the writ cinsiders to be the right of the petitioner and is in the interest of justice. It is not restricted to persons charged with judicial or quasi-judicial; duty only.
It is issued only when there is a specific legal right, but not specific legal remedy to enforce that right. It lies for restoration, admission and election to office of a public nature so long the office is vacant. It may, also, lie for the delivery, inspection and production of public books, papers and documents provided that the petitioner has a direct tangible interest in such books, paper and documents. It lies for the performance public duties which are not discretionary and compel public officials to perform such public duties.
Mandamus will not be issued when any alternative remedy by way of appeal or any other renedy under any other statute is available. Article 32 is limited to the enforcement of fundamental right of part III of the Constitution only.

# Certiorari 

The writ of Certiorari may be issued to any judge, Magistrate or person or body of person or authority vested with judicial or quasi-judicial functions. An order of Certiorari is an order directing the aforesaid authorities and requiring them to transmit the record of the proceedings in any cause or matter to the High Court to be dealt with there. It may be issued when the decision complained is of an authority having the legal duty to act judicially or quasijudicially, and the authority has either no jurisdiction, or there is an excess of jurisdiction. Mainly it is issued for quashing decisions only.

## Prohibition

The writ of prohibition is an order directed to an inferior Court or tribunal forbidding such Court or tribunal from continuing with the proceeding of any cause or matter. It is an appropriate writ 'to a tribunal which threatens to assume or assumes a jurisdiction not vested in it, so long as there is something in the proceeding s left to prohibit.'
The difference between a writ of Prohibition and Certiorari is that the former is issued to restrain a tribunal from doing an act before it is actually done, while the latter may be issue during the course of the proceeding of an act and even after the act is done and the proceeding is concluded. Both can be issued to the person, or body, or tribunal if charged with judicial or quasi-judicial duties.

## Quo Warranto

It is a writ questioning a right of a person holding an office of a public nature, and direct him to show an authority under which he is holding such office or exercising the right. In older days it lay against the crown who claimed or usurped any office, franchise or liberty for holding an enquiry by what authority he support his claim. Now, it may be issued any person holding the office of a public nature on the application of any person without alleging the violation of his any specific right. 
Any member of the public acting in good faith and whose conduct otherwise did not disentitle him to the relief can apply to the High Court for this writ. For instance, any registered graduate of any university can apply for the instance of this writ against any member of University Syndicate or Executive Council or Academic Council or any such other statutory body of that University. Likewise, a petition may lie against the Speaker, chairman or the parliament of state legislation or any other statutory or local bodies. If the opposite party fails to support his claim, he will be ousted from the office and may be ordered to pay fine and cost of the petition.


# WRIT PETITION (CIVIL) 

## IN THE HIGH COURT OF DELHI AT NEW DELHI (WRIT JURISDICTION)

## WRIT PETITION (CIVIL) NO. $\qquad$ OF2016

IN THE MATTER OF :
X $\qquad$ S/o $\qquad$ R/o $\qquad$ PETITIONER

VERSUS

Muncipal Corporation of Delhi,
Through Its Commissioner ... RESPONDENT

## WRIT PETITION UNDER ARTICLE 226 OF CONSTITUTION OF INDIA FOR ISSUANCE OF PREROGATIVE WRIT OF MANDAMUS OR ANY OTHER APPROPRIATE WRIT

Most Respectfully Showeth:

1. That the petitioner is a citizen of India residing at $\qquad$ . The respondent is Muncipal Corporation of Delhi having their office at Town Hall, Chandni Chowk, Delhi.

## BRIEF FACTS:-

2. That the petitioner is aggrieved by the illegal appointments of daily wage workers by the M.C.D. office in defiance of Notification No. MCD/LF/01-103 dated 1.2.2014 which requires the M.C.D. to appoint only those people as Daily wage worker who are below the age of 30 years as an 01.10.2014. The said Notification was issued after it was duly approved.
3. That the petitioner is of 27 yrs of age and was working as a daily wage worker, when on 1.12.2014 his services were terminated without notice/prior intimation. The Petitioner during his service worked to the satisfaction of his superiors. The respondent has appointed Sh. Ompal, Sh. Ram and Smt Maya in defiance of the said notification M.C.D./LF/01-/03 at 01.02.2014 as all the three people namely Om Pal, Sh. Ram and Smt. Maya are more than 30 years of age as on 01.10.2014. The about named persons were appointed in utter disregard of Notification. The respondent, however, removed the petitioner from service although petitioner met the requirements. That the Petitioner made representation to the respondent vide letter dated 1.12.2014, 2.1.2015 and also met the commissioner personally and apprised them of his grievance, however nothing materialized.
4. That in spite of oral and written representations the respondent have not cared to act and are maintaining stoic silence on the whole issue.
5. That the petitioner have thus approached the Hon'ble court on amongst others the following grounds:

## GROUNDS:

(a) Because the action of the respondent is contrary to law and good conscience.
(b) Because the action of the respondent is arbitrary, unreasonable, irrational and unconstitutional.
(c) Because the respondent have no right to play with the career of the petitioner.
(d) Because the petitioner was removed from job inspite of the fact that he was below age and fulfilled all requirements.
(e) Because the respondent appointed. Sh. Ompal, Sh. Ram and Smt Maya despite their being average and not meeting requirements of Notification No. MCD/LF/01-103 dated 1.2.2014.
(f) Because the action of the respondent is bad in law
(g) That the Petitioner craves, leave of this Honorable Court to add, amend, and alter the grounds raised in this petition.
6. That the cause of action in present case arose on 1.2.2014 when the respondent brought out the Notification No. MCD/LF/01-103 dated 1.2.2014., it further arose when on 1.12.2014 the petitioner was removed from job inspite of the fact that he was below age and fulfilled all requirements, it further arose when respondent appointed. Sh. Ompal, Sh. Ram and Smt Maya despite their being average and not meeting requirements of Notification No. MCD/LF/01-103 dated 1.2.2014; it further arose when representations were made to respondent orally and in writing on 1.12.2014, and 2.1.2015. The cause of action further arose when respondent did not act inspite of the fact having brought to their notice. The cause of action is continuing one.
7. That the Petitioner has no other alternative efficacious remedy except to approach this Hon'ble Court by way of this writ petition.
8. That the petitioner has not filed any other similar writ petition either before this Hon'ble Court or before the Supreme Court of India.
9. That there has been no undue delay in filing of this petition.
10. That the Hon'ble court has territorial jurisdiction to entertain the writ petition.
11. That the requisite court fee of Rs. 50/- has been affixed on this petition.

# PRAYER: 

The petitioner most humbly prays that this Hon'ble Court may be pleased to :-
(a) issue appropriate writ in the nature of mandamus or any other appropriate writ directing the Respondents to cancel the illegal appointment made in disregard of Notification No. MCD/LF/01-103 dated 1.2.2003 : and
(b) issue necessary directions to appointment of petitioner and
(c) issue any other further order/orders or direction/directions as this Hon'ble Court may deem fit and appropriate no the facts and the circumstances of this case.

Date:
Place:

PETITIONER
THROUGH
ADVOCATE

[NOTE: The petition will be supported by an affidavit]


# WRIT PETITION (CRL.) FOR ENFORCEMENT OF FUNDAMENTAL RIGHT 

## IN THE HIGH COURT OF DELHI, AT NEW DELHI WRIT PETITION (CRL.) NO. $\qquad$ OF 2016

IN THE MATTER OF:
Mr. $\qquad$
S/o Sh. $\qquad$ ,
R/o $\qquad$ .....Petitioner

Versus

1. Union of India,

Through
Secretary to the Govt. of India
Ministry of Finance,
Department of Revenue,
North Block, New Delhi-11001
2. The Joint Secretary (PITNDPS),
to the Government of India,
Ministry of Finance,
Department of Revenue,
Room No.26, Church Road,
R.F.A. Barracks,

New Delhi -110001
3. Director General,

Directorate of Revenue Intelligence
Delhi Zonal Unit, B-3 \& 4, $6^{\text {th }}$ Floor,
Paryavaran Bhavan, CGO Complex,
Lodhi Road, New Delhi-110003 .....Respondents

PETITION UNDER ARTICLE 226 AND 227 OF THE CONSTITUTION OF INDIA READ WITH SECTION 482 OF THE CODE OF CRIMINAL PROCEDURE, 1973 SEEKING ISSUANCE OF A WRIT OF MANDAMUS AND/OR ANY OTHER APPROPRIATE WRIT, ORDER AND/OR DIRECTION IN THE NATURE THEREOF, THEREBY DIRECTING THE RESPONDENTS TO PLACE ON RECORD THE DETENTION ORDER DATED 10.09.2013 PASSED IN RESPECT OF THE PETITIONER ISSUED UNDER SECTION 3(1) OF THE PREVENTION OF ILLICIT TRAFFIC IN NARCOTIC DRUGS AND PSYCHOTROPIC SUBSTANCES ACT, 1988 BY THE RESPONDENT NO.2, ALONGWITH GROUNDS OF DETENTION AND RELIED UPON DOCUMENTS AND SIMILAR MATERIAL IN RESPECT OF OTHER CO-ACCUSED PERSONS AND FURTHER SEEKING ISSUANCE OF A WRIT OF CERTIORARI AND/OR ANY OTHER APPROPRIATE# WRIT, ORDER AND/OR DIRECTION IN THE NATURE THEREOF, THEREBY QUASHING THE SAID DETENTION ORDER PASSED AGAINST THE PETITIONER 

<br> MOST RESPECTFULLY SHOWETH: 

1. That, vide the present petition the petitioner is challenging detention order dated 10.09.2013 issued under section 3(1) of the Prevention of Illicit Traffic in Narcotic Drugs and Psychotropic Substances Act, 1988 by the respondent no. 2 against him, in respect of which he has recently come to know, when some officials, claiming themselves to be police officials, visited his abovementioned premises in the first week of this month for its execution. It is worth mentioning here that similar detention orders were issued against even other co-accused persons, namely X and Y , which have been revoked on the recommendation of the Advisory Board, who did not find sufficient grounds for detention of those respective detenus. Copy of such a detention order bearing No. U-11011/1/2012- PITNDPS dated 10.09.2013 qua Mr. X is enclosed herewith as Annexure A. Copies of the grounds of detention passed in support of that detention order alongwith the list of relied upon documents are also enclosed herewith as Annexures B \& C respectively.
2. That the allegations, as revealed from the grounds of detention in respect of his said co-accused, are that the petitioner was involved with other accused persons, in the activities of acquiring, possessing, hoarding, selling and exporting NDPS items. It is respectfully submitted that all the allegations as made in the grounds of detention are false, frivolous and motivated ones, which is also apparent from bare reading of grounds of detention and the documents, said to be relied upon at the time of passing the impugned detention order, since even as per those allegations the petitioner has not committed any offence whatsoever under the Narcotic Drugs and Psychotropic Substances Act, 1985 (in short Act). It is further submitted that in order to falsely implicate the petitioner in the matter he was forced /coerced to make certain involuntary statements under section 67 of the Act, which have been duly retracted. Not only this, it is respectfully submitted that, the petitioner is made to understand that, even other co-accused were forced/coerced to make certain involuntary and incorrect statements from which even they have retracted at the first available opportunity.
3. That, the petitioner's case is fully covered by the exceptions, as laid down, by the Hon'ble Supreme Court in Alka Subhash Gadia's case. It is respectfully submitted that recently the Hon'ble Supreme Court in Deepak Bajaj vs. State of Maharashtra, 2010 (4) SCC (Cri) 122 has summarized the law on the issue as under:
(a) Five grounds mentioned in Alka Subhash Gadia case, on which Court can set aside detention order at pre-execution stage, are illustrative and not exhaustive. It was also reiterated that judgment of a court is not to be read mechanically as a Euclid's theorem nor as if it were a statute, hence, cannot be constructed as such.
(b) It was held that entertaining petition against preventive detention order at pre-execution stage should be an exception and not a general rule. However, if a person against whom a preventive detention order is passed comes to court at pre-execution stage and satisfies the court that such order is clearly illegal, there is no reason why the court should stay its hands and compel him to go to jail even though he is bound to be released subsequently because of illegality of such order. If a person, is sent to jail, then even if he is subsequently released, his reputation may be irreparably tarnished. Liberty of a persona is a precious fundamental right under article 21 and should not be lightly transgressed.
(c) Non-placement of retractions of confessional statement and other relevant material before detaining authority vitiates detention order even at pre-execution stage. Hence, on facts, it was held that, as relevant materials were not placed before detaining authority, it vitiated the detention order.
4. That, therefore, under these circumstances, it is respectfully submitted that the impugned detention order dated 10.09.2013 is highly illegal and a nullity in the eyes of law and the same is liable to be quashed on the following amongst other grounds which are without prejudice and in addition to each other.

# GROUNDS 

A. Because though the impugned detention order was passed on 10.09.2013, but till date the same has not been executed, despite the fact that throughout this period the petitioner was available at home and was attending all his daily routine activities. Not only this, it is further respectfully submitted that, the petitioner was regularly appearing before the Trial Court in the prosecution proceedings, launched at the instance of the sponsoring authority. It is submitted that the long and undue delay in execution of the impugned detention order creates doubt about the genuineness qua subjective satisfaction of the detaining authority in detaining the petitioner preventively. Therefore, in view of the exceptions of the Alka Subhash Gadia's case the impugned detention order is liable to be quashed. Copies of the relevant order sheet of the Trial Court in prosecution proceedings is enclosed herewith as Annexure D.
B. Because the petitioner says and submits that the alleged incident took place on 23/24.10.11, however, no detention order was passed till 10.09.13, which clearly shows that there has been long and undue delay in passing the impugned detention order, which has snatched the nexus between the purpose of detention and the allegations, as made in the grounds of detention. Therefore, it is apparent that the detention order has been passed on stale incident and on this ground also the impugned detention order is liable to be quashed, more particularly when similar detention orders under similar circumstances have already been revoked by the respondent no. 2, on the recommendation of the Advisory Board, who did not find sufficient cause for issuance of those detention orders.
C. Because since the date of the passing of the impugned detention order, which is for a period of one year only, the petitioner has not come to the adverse notice of any law enforcing authority. Therefore, under these circumstances, purpose of the said detention order has already been served and nothing would be achieved by sending the petitioner into custody pursuant to the impugned detention order, which was passed about more than $11 / 2$ year back for his detention for a period of one year. It is respectfully submitted that, under these circumstances, purpose of passing the impugned detention order is no more preventive. Therefore on this ground also the impugned detention order is liable to be quashed.
D. Because the petitioner/ detenu is a poor person and has clean antecedents. It is respectfully submitted that he is the sole bread earner of his family, which includes his old ailing parents, wife and minor children. It is further submitted that grave injustice has been done to the petitioner by executing the impugned detention order, which is even otherwisevery draconian in nature, being violative of principles of natural justice. It is submitted that, the impugned detention order is unconstitutional.
E. It is further respectfully submitted that initiation of mere prosecution proceedings were sufficient to prevent the petitioner from indulging in the alleged prejudicial activities. Therefore, on this ground also the impugned detention order is liable to be quashed.
F. Because the impugned detention order is not only contrary to the facts of the case but also contrary to the settled principles of law.
5. That, the annexures annexed with this petition are true copies of their originals.
6. That, no similar petition has been filed either before this Hon'ble Court or any other Court including the Hon'ble Supreme Court of India.
7. That, the petitioner has no other efficacious remedy other than to file the present petition.

# PRAYER: 

In view of foregoing it is most respectfully prayed that:
(i) a writ of mandamus and/or any other appropriate writ, order and/or direction in the nature thereof may kindly be issued thereby directing the respondents to place on record the abovementioned detention order, issued under section 3(1) of the Prevention of Illicit Traffic in Narcotic Drugs and Psychotropic Substances Act, 1988 (in short Act) by the respondent no. 2 against the petitioner dated 10.09.2013 alongwith the grounds of detention and relied upon documents, besides the similar material in respect of other co-accused/ detenus, who were detained earlier on the same set of facts and circumstances; and
(ii) further a writ of certiorari and/or any other appropriate writ, order and/or direction in the nature thereof may kindly be issued thereby quashing the abovementioned detention order dated 10.09.2013, passed by the respondent no.2; and/or
(iii) any other order, as may be deemed fit and proper under the facts and circumstances of the case may also be passed in the matter in favour of the petitioner and against the respondents.


New Delhi
Dated:

Petitioner
Through
Advocates


# SPECIAL LEAVE PETITION (CIVIL) 

Article 136 of the Constitution of India vests the Supreme Court with the power to grant Special leave to appeal against any decree, order or, judgement in any cause or matter passed by any court or tribunal in the country.

IN THE SUPREME COURT OF INDIA
CIVIL APPELLATE JURISDICTION
ORDER XXI, Rule 3(1) (a), SUPREME COURT RULES 2013
(Under Article 136 of the Constitution of India)
SPECIAL LEAVE PETITION (CIVIL) No. OF 2016
(Arising out of Judgment and order dated 14.12.2015 passed in Writ Petition No. 5427 of 2004 by Hon'ble High Court of Judicature of Bombay Bench at Aurangabad)

Between

Position of the Parties

In the High Court In this court

Vasant S/o Shankar Bhavsar
Age: Major, Occu:
Residing at \& Post Faijpur,
Taluka Yawal, Dist: Jalgaon. ...

Petitioner Petitioner

AND

1. D $\qquad$ S/o $\qquad$ , $\qquad$ ,
R/o $\qquad$ , $\qquad$ ,
Taluka: Bhusawal, Dist: $\qquad$

Contesting Respondent    Contesting Respondent

2. H $\qquad$ S/o $\qquad$ , $\qquad$ ,
R/o $\qquad$ , $\qquad$ ,
Taluka: Bhusawal, Dist: $\qquad$

Contesting Respondent    Contesting Respondent

3. C $\qquad$ S/o $\qquad$ , $\qquad$ ,
R/o $\qquad$ , $\qquad$ ,
Taluka: Bhusawal, Dist: $\qquad$

Contesting Respondent    Contesting Respondent

4. P $\qquad$ S/o $\qquad$
R/o: $\qquad$ , $\qquad$ ,
Dist: $\qquad$ ...

Contesting Respondent    Contesting Respondent

## SPECIAL LEAVE PETITION UNDER ARTICLE 136 OF CONSTITUTION OF INDIA

To
The Hon'ble Chief Justice of India and His Companion Justice of the Supreme Court of India.

The humble petition of the petitioner above named most respectfully showeth:

1. That the present petition has been filed seeking special leave to appeal in the final judgment and order dated 14.9.2012.201508 of the Hon'ble High Court of Judicature of Bombay Bench at Aurangabad in Civil Writ Petition No. 5427 of 2004 titled "Vasant S/o Sh. Shankar Bhavsar Versus Digambar \& Ors." which was dismissed by the Hon'ble High Court.

# 2. QUESTIONS OF LAW: 

That the following questions of law arise for consideration herein:
a) Whether in the facts and circumstances of the case the Hon'ble High Court was justified in dismissing the Civil Writ Petition

## 3. Declaration in terms of Rule 3 (2):

That the Petitioner states that no other petition for special leave to appeal has been filed by him against the judgment and order impugned herein.

## 4. Declaration in terms of Rule 5:

The Petitioner states that the Annexures filed along with the special leave petition are true copies of the pleading's and documents which formed part of the records of the case in the court below against whose order the leave to appeal is sought for in this petition.

## 5. GROUNDS:

That the special leave to appeal is sought on the following grounds:
I) Because the High Court had erred in passing the impugned judgment.
II) Because the High Court could not have allowed the errors to prevail by dismissing the writ petition.
III) Because the impugned judgments and orders of Hon'ble High Court and of Maharashtra Revenue Tribunal, Mumbai, dated 24.10.1997, of the Sub-Divisional Officer, Bhusawal dated 31.3.1997, of Tehsildar and Agricultural Lands Tribunal, Yawal, dated 1.10.1996 suffer from error apparent on the face of record.
IV) Because the reasoning of the authorities mentioned above that the will executed by Vishnu on 7.1.1968, the original tenant and owner under the Bombay Tenancy Act; and the registered Hakka Sod Patrak dated 18.12.1981 executed by Digambar S/o Vishnu do not come in the definition of transfer as envisaged in Section -43 of the Bombay Tenancy Act, is unsustainable in law.
V) Because with respect to the Authorities below that the incidents of transfer mentioned in Section 43 of Bombay Tenancy Act viz. sale, Gift, Exchange, mortgage, lease, assignment or partition are not the only incidents of transfer to be considered in reference to Section 43 of the Act but they are only mentioned by way of examples. It does not mean the other incidents of transfer like will or Hakka Sod Patrak do not amount to transfer and are not to be considered by the authorities under the Bombay Tenancy Act.
VI) Because the ground No. V above is further supported by other provisions of Bombay Tenancy Act. For example Section 32-R lays down that purchaser U/s. 32 of the Act is to be evicted if he fails to cultivate land personally. Section 43 of the Act lay down restrictions on the purchaser not to transfer the purchased land under the Act without the sanction of the Collector. Section 43 (2) of the Act says "any transfer or partition of land in contravention of Sub-Section (1) shall be invalid". Section 70 (mb) lays down a duty on Mamlatdar to decide U/s. 48B or 84 C whether a transfer or acquisition of land is invalid and to dispose off land as provided in Section 84 C. Section 83 A (1) lays down that no person shall acquire land by transfer which is invalid under any of the provisions of the Act. Section 83 A(2) lays down that a persons acquiring land by invalid transfer shall be liable to consequences as laid down in Section 84 or 84 C of the Act. Section 84 of the Act provides for summary eviction of unauthorised or wrongful occupant of the land. Section 84 C of the Act gives authority to the Mamlatdar to hold enquiry of any such illegal transfer and to decide it accordingly. Section 84 C (3) lays down that land declared to be invalidly transferred to vest in the State. Section 84 C (1) gives the power to the Collector to dispose the land which are declared to be invalidly transferred.
VII) Because in the Section 32 R, 43 (1), 43 (2), Section 70 (mb), Section 83 A (1), 83 A (2), Section 84, 84 C, 84 C(3) and 84 CC (1) of the Bombay Tenancy Act, at many places the words "any transfer" are used as these sections are having wider scope covering all types of transfers, and not only to the six kinds of transfers mentioned in Section 43 of the Act. Therefore the reasoning of these authorities below that the will and Hakka Sod Patrak are not covered by Section 43 of the Act do not stand good in law.
VIII) Because the will and registered Hakka Sod Patrak have resulted into permanent transfer in perpetuity of this land purchased by the tenant U/s 32 of the Act, without sanction from the Collector U/s. 43 of the Act and therefore the application filed U/s 43 read with section 84 C of the Act was liable to be allowed completely.
IX) Because the definition of transfer as given in Section 5 Chapter II in Transfer of property Act is totally neglected by the learned three authorities below.
X) Because the learned authorities below have not taken into consideration all the circumstances of this case while deciding the matter.
XI) Because the judgments and orders of three authorities below are contrary to law and good conscience.
XII) The petitioner crave, leave of this Honorable Court to add, amend, and alter the grounds raised in this petition

# 6. GROUNDS FOR INTERIM RELIEF: 

A. That the petitioner apprehends that the respondents may sell, alienate or part with the property illegally.

## 7. MAIN PRAYER:

Wherefore, it is respectfully prayed that this Hon'ble Court may kindly be pleased to:
a) Grant the special leave petition from the final judgment and order dated 14.12.2015 of the Hon'ble High Court of Judicature of Bombay Bench at Aurangabad in Civil Writ Petition No. 5427 of 2015 titled "Vasant S/o Sh. Shankar Bhavsar Versus Digambar \& Ors." And
b)Be pleased further to pass such other order or orders as deemed fit and proper in the facts, reasons and other attending circumstances of the case.

# PRAYER FOR INTERIM RELIEF: 

(a) It is prayed that interim directions be issued to the Respondent may be directed not to sell, alienate or part with the property. Gat No. 2752 comprising of Survey No. 638/1, 638/3-A, 639/1, 639/3 area measuring 2 Hectares 87 Ares situated at village Nhavi, Taluka Yawal.
(b)Be pleased further to pass such other order or orders as deemed fit and proper in the facts, reasons and other attending circumstances of the case.
AND FOR THIS ACT OF KINDNESS THE PETITIONER SHALL EVER REMAIN GRATEFUL AS IN DUTY BOUND

New Delhi
Date of drawn:
Date of filing:

Drawn and Filed by:
Advocate for the Petitioner

[NOTE : To be supported by an affidavit]


# SPECIAL LEAVE PETITION (CRIMINAL) 

## IN THE SUPREME COURT OF INDIA (CRIMINAL APPELLATE JURISDICATION) ORDER XXII, Rule 2(1), SUPREME COURT RULES 2013

(Under Article 136 of the Constitution of India)
SPECIAL LEAVE PETITION (CRL) No. $\qquad$ OF 2016
(FROM THE FINAL JUDGEMENT AND ORDER DATED $\qquad$ PASSED BY THE HIGH COURT OF $\qquad$ AT $\qquad$ IN CRIMINAL APPEAL NO. $\qquad$ OF $\qquad$ )

IN THE MATTER OF:-
N. $\qquad$ S/o $\qquad$ ,
$\mathrm{R} / \mathrm{o}$ $\qquad$ .
lodged in Model Jail, Chandigarh

... PETITIONER/ ORIGINAL ACCUSED.

## VERSUS

1. Union Territory of $\qquad$
through Home Secretary,
Secretariat, $\qquad$ 

... RESPONDENT

2. S Singh S/o $\qquad$ R/o $\qquad$ . 

... PROFORMA RESPONDENT/ ORIGINAL ACCUSED.

## PETITION FOR SPECIAL LEAVE TO APPEAL UNDER ARTICLE 136 OF THE CONSTITUTION OF INDIA

To,
The Hon'ble Chief Justice of India
And his Companion Justices of
The Supreme Court of India
The humble petition of the above named petitioner most respectfully showeth:

1. That the present Special leave Petition (Criminal.) is filed against order dated 26.11.2015 of the High Court of Punjab and Haryana at Chandigarh, in Criminal Appeal No. 305-DB of 2013, titled "Subeg Singh versus The State Union Territory of Chandigarh" whereby the Hon'ble Court dismissed the appeal of the petitioner.
2. That the present petition raises an important question of law for consideration before this Hon'ble Court. $\qquad$ .
3. Declaration under Rule 2(2) - That the Petitioner states that no other petition for special leave to appeal has been filed by him against the judgment and order impugned herein.
4. Declaration under Rule 4- The Petitioner states that the Annexures filed along with the special leave petition are true copies of the pleading's and documents which formed part of the records of the case in the court below against whose order the leave to appeal is sought for in this petition.

# 5. BRIEF FACTS 

On the night intervening 11/12.2.2013 murder of Shri Bachna Ram, who was a cook and domestic servant of Shri Devinder Singh Brar, resident of house No. 53, Sector 28-A Chandigarh, was committed in the kitchen of his house when Shri Devinder Singh Brar and his sister Smt. Gurmail Kaur were in Aurngabad. The F.I.R. was registered on the statement of Capt Jagat Pal Singh PW-11 who resides in the neighborhood of house No. 53. The offence came into light when Smt. Babita the sweeper of House No. 53 informed Capt. Jagat Pal Singh PW-11. On the information given by Catpain Jagat pal Singh, PW-11 S.I. Puran Chand aforesaid recorded D.D.R. No. 46 dated 13.2.2013 in the Rojnamcha of the police-Station East, Chandigarh and formed a Police party and came to House No. 53. The investigation of this case remained pending with S.I. Puran Chand up to 8.3.2013. The police remained unsuccessful in tracing out the crime till 8.4.2013. On that day, Balwan Singh S.I. PW-24 of the CIA staff, took over the investigation of this case. He along with members of the police party including S.I. Partap Sing PW-23 visited House No. 53. Sector 28-A Chandigarh where Mr. Devinder Singh Brar PW-12 was present. In his presence, appellant Gurdev Singh was interrogated and he made certain disclosures after which the further story unfolded. After completion of the investigation the accused were challaned on the charges under Section 120B, 392/120-B, 302/34, 302/114, I.P.C. The accused pleaded not guilty to the charge framed against them and claimed trial. The Court of Sh. B.S.Bedi, Session Judge, Chandigarh convicted the accused U/s. 120-B, 302/34 and in alternative 302/114 IPC.
5. That the copy of the Trial Court judgment passed by Sessions Judge Chandigarh convicting and sentencing the petitioner in Sessions Case No. 15 of 2013 U/s. 120-B, 302/34 and in alternative 302/114 IPC is Annexure P-1.

## 7. GROUNDS

Being aggrieved and dissatisfied with the impugned order, the Petitioner approaches this Hon'ble Court by way of Special Leave Petition on the following amongst other grounds:-
A. Because the judgment and order dated 26.11.2015passed by the Hon'ble High Court which dismissed the appeal of the appellant is contrary to law and facts and hence the same is liable to set aside both on the point of law and equity.
B. Because the prosecution only produced the partisan or the interested persons as witnesses in order to prove the commission of crime by the petitioner. This fact doubts the truthfulness of the case of prosecution.
C. Because the prosecution has suppressed the origin and genesis of the occurrence and has thus not presented the true version.
D. Because the prosecution has miserable failed to prove its case beyond doubt against the petitioner.
E. Because the witnesses have not deposed correctly and there is discrepancy in the depositions of witnesses and the conviction of the petitioner is bad.
F. Because the Hon'ble Court ignored the fact to be considered in the case was as to whether the evidence of PW-5 Gurpartap Singh, the approver, was reliable and if so whether there was corroboration to his evidence on material particulars so as to warrant conviction. It is high-lighted that it was a case of no evidence from the side of the prosecution and, therefore, the evidence of the approver and other circumstances, corroborated by his statement cannot be the base of conviction of the appellant.
G. Because Gurpartap Singh PW-5 lost his status as an approver when he appeared before the learned Committing Magistrate and his statement was recorded as PW-1 on 11.9.1995. The relevant portion of the same is as follows:-
"Before 7.4.2012 I had no conversation with anybody. On 7.4.2012 my self, accused Subeg Singh and accused Nand Singh were coming from Rajpura to Chandigarh on a Motorcycle. I had come to Chandigarh on that date for the first time. When we crossed Zirakpur, we were apprehended on the first Chowki by the Chandigarh Police. From there we were apprehended and implicated in this case. I do not know where Sector 28 is. I was threatened by the Police that I should give a statement in favour of the Police otherwise I would be involved in a TADA case and should suffer imprisonment for whole of the life. In the Jail also, the police people used to visit me and threaten and intimidate me. I made statement before the Chief Judicial Magistrate on account of fear of the police. I have nothing more to say about this Case"
H. Because the above statement will show that the tender of pardon given to Gurpartap Singh by the Learned Chief Judicial Magistrate, Chandigarh on 1.5.2012 was no, more available and he lost the status of an approver. It is stated here that the Learned Committing Magistrate was entirely wrong in permitting the cross-examination of Gurpartap Singh by the prosecution by declaring him hostile. This could not have been done for the simple reason that he did not attain the status of a witness. This being so, all the proceedings after 11.9.2012 with regard to the examination of Gurpartap Singh as a witness by the Learned committing Magistrate or by the Learned Sessions Judge, Chandigarh stood vitiated being totally illegal. It is submitted that from the date 11.5.2012 when Gurpartap Singh made the above statement, he is to be taken as an accused and not an approver, he had made altogether different statement from the one alleged to have been made after alleged acceptance of tender of pardon.
8. Grounds for interim relief

# 9. PRAYER 

The Petitioner herein prays that this Hon'ble Court may graciously be pleased to:
a) Grant special leave to appeal to the petitioner against judgment and order dated 26.11.2015 of the High Court of Punjab and Haryana at Chandigarh, in Criminal Appeal No. 305-DB of 2013, titled "Subeg Singh \& Anr., versus The State Union Territory of Chandigarh"
b) Pass any other order which this Hon'ble Court may deem fit and proper in the facts and circumstances of the case in favour of the Petitioner.
11. Prayer for interim relief

DRAWN AND FILED BY
ADVOCATE FOR THE PETITIONER

NEW DELHI
DRAWN ON: $\qquad$
FILED ON: $\qquad$

[NOTE: To be supported by an affidavit]


# PLEADINGS UNDER CRIMINAL LAW <br> APPLICATION FOR GRANT OF BAIL 

## IN THE COURT OF METROPOLITAN MAGISTRATE (DISTRICT <br> $\qquad$ <br> DELHI <br> BAIL APPLICATION NO. $\qquad$ OF 2017

## IN THE MATTER OF:

X $\qquad$
S/o $\qquad$
R/o $\qquad$ 

.....APPLICANT

VERSUS

STATE

....RESPONDENT/COMPLAINANT

FIR NO. $\qquad$
U/S $\qquad$
POLICE STATION $\qquad$

## APPLICATION FOR GRANT OF BAIL UNDER SECTION 437 OF CODE OF CRIMINAL PROCEDURE, 1973

Most Respectfully Showeth:

1. That the accused above named was arrested by the police on ...... and is in judicial custody since then. It is alleged that on......, the accused was suspiciously moving on Baba Kharak Singh Marg, New Delhi when the police apprehended him, conducted the search and recovered 3 gms . of smack from his pocket.
2. That the accused has been falsely implicated in the instant case and he has nothing to do with the alleged offence.
3. That nothing was recovered from the possession of the accused or at his instance and the so called case property has been planted upon the accused.
4. That the accused is a law abiding citizen and belongs to a very respectable family. He has never indulged in any illegal activities and commands respect and admiration his locality.
5. That on.......(date), the accused found some persons selling smack near Hanuman Mandir Cannaught Place, New Delhi. The accused immediately reported the mater to police as the result of which police also arrested some of the persons. Since that time, those persons who were arrested at the instance of the accused, were threatening the accused to falsely implicate him in a criminal case in collusion with police. The accused made a complaint in this regard to the Dy. Commissioner of Police, true copy of which is annexed hereto as Annexure-A.
6. That after the said complaint, the accused was called by the Vigilance Department, Delhi Police who enquired into his complaint. True copy of the said notice issued by the Vigilance Cell is enclosed herewith as Annexure-B.
7. That it is unimaginable that the accused who made a complaint against the sellers of smack, would himself indulge in such activities.
8. That the accused is a permanent resident of Delhi and there are no chances of his absconding in case he is released on bail.
9. That there is no chance of the accused absconding or tempering with the prosecution evidence in the event of reLease on bail.
10. That the accused undertakes to join the investigation as and when directed to do so.
11. That the accused is not a previous convict and has not been involved in any case of this nature except the present case.
12. That the present case is a result of clear manipulation by the police.
13. That the accused from all accounts is an innocent person.

# PRAYER: 

It is therefore respectfully prayed that the accused may kindly be released on bail during the pendency of this case.

Place:
Date:

APPLICANT
THROUGH
ADVOCATE

Note: To be supported by affidavit of Pairokar and Vakalatnama duly attested by Jail Authorities.


# APPLICATION FOR THE GRANT OF ANTICIPATORY BAIL IN THE COURT OF SESSIONS JUDGE (DISTRICT <br> $\qquad$ ), DELHI TIS HAZARI COURTS DELHI 

## ANTICIPATORY BAIL APPLICATION NO. $\qquad$ OF 2017

## IN THE MATTER OF;-

X $\qquad$
S/o $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$ 

... APPLICANT

VERSUS

STATE

...RESPONDENT/COMPLAINANT

FIR NO. $\qquad$ OF 2017
UNDER SECTION $\qquad$
POLICE STATION $\qquad$

## APPLICATION FOR THE GRANT OF ANTICIPATORY BAIL UNDER SECTION 438 OF THE CODE OF CRIMINAL PROCEDURE, 1973

Most Respectfully Showeth:

1. That the Applicant is a youngman aged 20 years residing at $\qquad$ Delhi. He is also a Director of M/s. ABC Ltd. which is a very leading company engaged in the manufacture of electrical appliances.
2. The Applicant is a very respectable person of his locality and is a peace loving citizen.
3. That the Applicant was on friendly terms with Miss Y major daughter of the Complainant. However, the relationship of the Applicant with Miss Y was not liked by her family members so much so that they had stopped Y from meeting the Applicant and had threatened her that in case she meet the Applicant, they will implicate the Applicant in some false criminal case.
4. That Miss. Y had also written number of letters to the Applicant calling upon him to marry her as she had feared that her family members may sabotage her relationship with the Applicant, which shows that family members of Miss. Y were deadly against the Applicant and were looking for some opportunity to falsely implicated him in some false criminal case in order to pressurize him to severe his relationship with Y.
5. That on $\qquad$ (date), the Applicant had gone to meet his friend, who is residing in the neighborhood of Miss Y. When the Applicant reached the house of his friend, he was suddenly attacked by father, uncle and brother of Miss Y as a result of which he fell down and sustained abrasion/injuries. The Applicant's friend came to the rescue of the Applicant and with great difficulty; the Applicant was saved from the clutches of Miss Y's family members by other neighbors and passersby.
6. That the police has registered a false FIR against the Applicant. A bare perusal of the said FIR reveals that the brother of Miss Y attacked the Applicant and not vice-versa. As a mater of fact, the aggressor has manipulated with the police and has falsely implicated the Applicant. The Applicant is in fact the victim at the hands of the Complainants who have conspired with the police and got this case registered against them. The photostat copies of the letters written by Miss Y to the Applicant are annexed herewith.
7. That the FIR registered against the Applicant is absolutely false and incorrect. The Applicant is not at all involved in the alleged offence and has been falsely implicated by the police.
8. That the Applicant apprehends that he may be arrested in pursuance of the aforesaid false and fictitious complaint.
9. That the police officials have visited the premises of the Applicant in his absence and there is every likelihood of his being arrested in the instant case.
10. That the Applicant undertakes to join the investigation as and when directed to do so.
11. That the Applicant is a permanent resident of Delhi and there is no chance of his absconding in case he is granted anticipatory bail.
12. That the Applicant has never been involved in any criminal case except the present one.

# PRAYER: 

It is, therefore most respectfully prayed that the Applicant be released on bail in the event of his arrest and appropriate directions in this regard may please be sent to the concerned Investigating officer/S.H.O. Any other order/orders which this Hon'ble Court may deem fit and proper on the facts and circumstances of this case may also be passed.

Place:
Date:

APPLICANT
THROUGH
ADVOCATE

[Note: To be supported by affidavit]


# COMPLAINT UNDER SECTION 138, THE NEGOTIABLE INSTRUMENTS ACT 

## IN THE COURT OF CHIEF METROPOLITAN MAGISTRATE, .....COURT (DISTRICT <br> $\qquad$ ), DELHI

CRIMINAL COMPLAINT NO. $\qquad$ OF 2017
$\mathrm{X}$ $\qquad$
S/o $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$ 

...COMPLAINANT

VERSUS

Y $\qquad$
S/o $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$ 

...ACCUSED

JURISDICTION : P. S. $\qquad$

## COMPLAINT UNDER SECTION 138 OF THE NEGOTIABLE INSTRUMENTS ACT, 1881

## MOST RESPECTFULLY SHOWETH:

1. That the Complainant is the owner and landlord of flat bearing No. $\qquad$ , New Delhi.
2. That the accused is a tenant under the Complainant in respect of flat bearing No. $\qquad$ New Delhi, comprising of two bed-rooms, drawing-cum-dining room, study room, kitchenroom, two bathrooms-cum-toilets and a terrace at a monthly rent of Rs. 2500/- for residential purposes w.e.f. $\qquad$ . True copy of the Lease-deed dated $\qquad$ is annexed hereto as Annexure - 'A'
3. That on $\qquad$ the accused handed over cheque bearing Nos. $\qquad$ dated $\qquad$ for Rs. $\qquad$ drawn on $\qquad$ Bank, New Delhi to the complainant towards rent of the said premises for the months of September, October and November, ...... the said original cheque is annexed hereto as Annexure - B.
4. That the Complainant deposited the said cheque in his account with the $\qquad$ (bank name) on $\qquad$ (date) but the same was dishonoured on presentation with the remarks 'REFER TO DRAWER'. The original returning memos dated $\qquad$ in respect of the said cheque is annexed hereto as Annexure - ' C '.
5. That vide letter dated......., the Complainant called upon the accused to make the payment of the amount covered by the dishonoured cheque. The said letter was sent to the accused by Regd. A.D. as well as U.P.C. However, the accused failed to make the payment of the amount in question to the Complainant.
6.That the cheque in question were returned unpaid because the amount standing to the credit in the Accused's account was insufficient to honour the cheque in question and as such the Accused is liable to be prosecuted an punished under Section 138 of the Negotiable Instruments Act, 1881 as amended upto-date.
7. That the Complainant has complied with all the requirements of Section 138 of the Negotiable Instruments Act, 1881 as amended upto-date namely the cheque in question were presented on $\qquad$ i.e. within the period of its validity, the demand for payment was made to the Accused on $\qquad$ i.e. within thirty days of the date or receipt of information regarding the dishonouring of the cheque. True copy of the said demand dated $\qquad$ is annexed hereto as Annexure - 'D'. The postal receipt and the U.P.C. thereof are annexed hereto as Annexure-E collectively. The accused failed to make the payment within fifteen days of the said notice and as such the Complainant has approached this Hon'ble court within one month of the date of the cause of action. The Compaint is therefore within time.
8. That the Hon'ble Court has jurisdiction to entertain and try the present complaint because the offence is committed within the jurisdiction of this Hon'ble Court. (Mention how the court has jurisdiction based on the facts).

# PRAYER: 

It is, therefore most respectfully prayed that his Hon'ble Court may be pleased to summon the accused under Section 138 of the Negotiable Instruments Act, 1881 as amended upto-date and the accused be tried and punished in accordance with law for the aforesaid offence committed by him.

Place 
Date

COMPLAINANT
THROUGH
ADVOCATE

Note : List of witnesses to be mentioned at the end of the complaint or separately after writing short title of the complaint case -

1. Complainant;
2. Banker(s) of the complainant with record of the cheque.
3. Banker(s) of the accused with record of the cheque
4. Any other witness, if needed, as per the facts of the case


# APPLICATION FOR MAINTENANCE UNDER SECTION 125 OF CRPC, 1973 

## IN THE COURT OF PRINCIPAL JUDGE, FAMILY COURT, DELHI.

## MAINTENANCE APPLICATION NO. $\qquad$ OF 2017

IN THE MATTER OF:
1.Smt. X $\qquad$
W/o Z $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$
2.Master R
S/o Z $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$
through his mother and natural guardian Smt X

APPLICANTS

VERSUS
Z $\qquad$
S/o $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$

RESPONDENT

## APPLICATION UNDER SECTION 125 OF THE CODE OF CRIMINAL PROCEDURE, 1973

Most Respectfully Showeth:

1. That the Applicant No. 1 is the legally wedded wife of the Respondent while Applicant No. 2 is the legitimate son of the Respondent.
2. That the Applicant No. 1 was married to the Respondent according to the Hindu Rites and ceremonies on $\qquad$ (date) at New Delhi and the Applicant No. 2 was born out of their wedlock on $\qquad$ . The Applicant No. 2 is staying with Applicant No. 1 at present.
3. That Applicant No. 1 and Respondent stayed together after their marriage and for the last two years proceeding $\qquad$ , they were staying at Delhi.
4. That sometime during the period June-July, $\qquad$ , the matrimonial life of the Applicant No. 1 and the Respondent got disturbed on account of the illegitimate affair of the Respondent with a girl named Mrs. A. The Applicant No. 1 made best possible efforts to persuade the Respondent to desist from indulging in an affair outside their wedlock. However, the same had no effect on the Respondent. Rather, the behavior of the Respondent towards Applicant No. 1 became rude, cruel and oppressive, and finally on $\qquad$ , the Respondent compelled the Applicant No. 1 to leave the matrimonial home along with Applicant No. 2, since then, the Applicants are staying with Applicant No. 1's father.
5. That the Applicant No. 1 has made repeated attempts to join the Respondent in the matrimonial home. However, the Respondent has refused to take back the Applicants and has clearly informed Applicant No. 1 that he was planning to marry Mrs. A though the same is not permissible under law. As such, the Respondent has deserted the Applicants without any reasonable cause.
6. That the Respondent is liable to maintain the Applicants who have repeatedly requested the Respondent to provide them the appropriate maintenance. However, the Respondent has not only refused/neglected to maintain the Applicants, but has also refused to ever part with/return the articles belonging to Applicant No. 1 towards the dowry and Stridhan which are lying at the Respondent's house.
7. That the Respondent is a man of status and is working as a Wing Commander in Indian Air Force. He is getting monthly emoluments of about Rs. $\qquad$ per month and as such has sufficient means to maintain himself and the applicants. He has no encumbrances or liabilities except that of maintenance of the applicants.
8. That the Applicant No. 1 has no independent source of livelihood and as such is unable to maintain herself. She is staying with her father at Delhi and as such both the Applicants are dependant upon him.
9. That the Applicant No. 2 is a minor and is also staying with the Applicant No. 1. He is studying in Delhi Public School, New Delhi, and his monthly expenditure including school fees, dresses etc. is more than Rs. $\qquad$ Apart form this, the Applicant No. 1 has also kept a maid to properly look after the Applicant No. 2 and is paying her Rs. $\qquad$ per month which is presently being borne by her father.
10. That the Applicants are residing at Delhi. This Hon'ble Court therefore is competent to entertain and try this petition.

# PRAYER: 

It is, therefore, most respectfully prayed that the orders for maintenance of the Applicants be passed and against the Respondent directing the Respondent to pay the monthly allowance of Rs. $\qquad$ towards the maintenance of the Applicant No. 1 and Rs
$\qquad$ towards the maintenance of the Applicant No. 2. The costs of these proceedings be also awarded to the applicants.

Place:
Date:

APPLICANTS
THROUGH
ADVOCATE

(Note :- An affidavit is to be attached to this petition)
Note: List of witnesses to be mentioned at the end of the complaint or separately after writing short title of the complaint case.


# OTHER PLEADINGS 

## COMPLAINT UNDER THE CONSUMER PROTECTION ACT, 1986

## BEFORE THE DISTRICT CONSUMER DISPUTES REDRESSAL FORUM (DISTRICT <br> $\qquad$ <br> CONSUMER COMPLAINT NO. <br> $\qquad$ OF 2017

IN THE MATTER OF:-
D $\qquad$
S/o Shri $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$

VERSUS

1. District Manager, Telephones
$\qquad$ .
2. Sub-Divisional Officer Phones,
...OPP. PARTY NO. 1
...OPP. PARTY NO. 2

## COMPLAINT UNDER SECTION 12 OF THE CONSUMER PROTECTION ACT, 1986

## MOST RESPECTFULLY SHOWETH:

1. That the Complainant is a subscriber of telephone no. $\qquad$ prior to $\qquad$ number whereof was $\qquad$ .
2. That the Complainant telephone went out of order on $\qquad$ . Several complaints were lodged with the department concerned which did not yield any result.
3. That a written complaint was lodged by him in the office of the opposite party No. 1 on $\qquad$ and also on $\qquad$ He then approached personally to the Sub-Divisional Officer Phones $\qquad$ and filed a written complaint with him on $\qquad$ . On $\qquad$ his telephone line was made operational.
4. That on $\qquad$ , the communication system installed at the residence of the complainant was again found paralysed. The matter was again reported to the department. Authorities did not take any action. He then lodged a written complaint in the office of the opposite party No. 2 on $\qquad$ . It did not find any response from the opposite parties. Another written complaint was lodged in the office of the opposite party No. 2 on $\qquad$ . It also remained unattended. Complainant then moved to the opposite party No. 1 and presented before him a written complaint on $\qquad$ whereafter the telephone service of the complainant was revived on the same day after continuous 24 days fault in the line.
5. That the complainant paid his telephone bill dated $\qquad$ amounting to Rs. $\qquad$ on $\qquad$ vide receipt No. $\qquad$ . On $\qquad$ he was asked by the Opposite Party to pay bill dated $\qquad$ by $\qquad$ failing which telephone connection was liable to be disconnected by 5 p.m. same day. The complainant never received bill dated $\qquad$ till date in original. He approached the opposite party for a duplicate bill dated $\qquad$ when he was told by him that another bill dated $\qquad$ be paid on the same day itself without which the payment of bill dated $\qquad$ would not be accepted. Request of the complainant to trace and produce receipt of payment of bill dated $\qquad$ was turned down by the opposite parties and the complainant was forced to pay both the bills on $\qquad$ although the bill dated $\qquad$ stood paid vide receipt No. $\qquad$ dated $\qquad$ .
6. That bill dated $\qquad$ charged Rs. $\qquad$ on account of rent from $\qquad$ to $\qquad$ . Bill dated $\qquad$ charged for rent from $\qquad$ to $\qquad$ . Thus applicant has been charged rent for the month of July $\qquad$ twice.
7. That on account of dereliction of duty and negligence on part of the opposite parties No. 1 and 2 the complainant suffered loss and injury due to deprivation, harassment, mental agony and loss of professional practice and for which he is entitled to compensation and refund of excess amount charged by the department.
8. That the complainant sent a notice to each of the opposite parties by registered post asking them to pay him a sum of Rs. $\qquad$ which now stands to Rs. $\qquad$ along with interest thereon till date of the actual payment to which none of them responded.
9. That in the interest of justice the complainant should be paid by the department through the opposite parties as under:
(1) Compensation of Rs. $\qquad$ @ per day for 69 days during which the telecommunication system remained paralysed, for the loss and injury caused to the complainant due to negligence and derelication of duly on the part of the opposite parties.
(2) Payment of Rs. $\qquad$ as stated in para 5 hereto along with interest @ $12 \%$ p.a. till the date of actual payment.
(3) Payment of Rs. $\qquad$ as refund of rental for 69 days as stated in paras 2,3 and 4 thereof.
(4) Payment of a sum of Rs. $\qquad$ being amount of rent for the month of July charged by the opposite parties twice as stated in Para. 6 hereto.
(5) Payment of a sum of Rs. $\qquad$ towards cost of notices including charges for stationary postage etc., given tyo the opposite parties.
10. That in support of the above averments and claims documents have been enclosed alongwith this complaint.
11. That the cause of action arose on $\qquad$ when the telephone of the complainant went out of the order and the system remained disputed for long 60 days merely due to the dereliction of duty and negligence of the opposite parties.
12. That for the purposes of Section 11 of the Act compensation claimed by the complainant is below Rs. $\qquad$ so this Forum has jurisdiction to determine and adjudicate upon this consumer dispute.
13. That there is a duty cast upon the District Manager Telephones, the opposite party No. 1 and the officials working under him to maintain trouble free service of the communication system installed at the premises of the complainant and to which they have miserable failed which has put the complainant to great deal of inconvenience, expense and mental agony.
14. That in the interest of justice the claims of compensation and refund should be allowed and also the interest as stated here before

# PRAYER: 

It is therefore, most respectfully prayed that this petition be kindly allowed, an amount of Rs $\qquad$ and interest wherever due be declared payable to the complainant by the opposite parties and the Opposite parties be directed to pay the amount as aforesaid to the complainant within 30 days of the Hon'ble Forum

Date:
Place:

Complainant
Through
Advocate

Note : An affidavit in suport to be annexed

As and when the Consumer Protection Act, 2019 is enforced, the pleading in terms of jurisdiction and other facets should be modified.


# CONTEMPT PETITION <br> IN THE HIGH COURT OF DELHI AT NEW DELHI 

CONTEMPT PETITION NO. $\qquad$ OF 2017
IN
CIVIL WRIT NO. $\qquad$ OF $\qquad$ 2003

## IN THE MATTER OF :

1. X $\qquad$ S/o $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$ , New Delhi
2. Y $\qquad$ W/o $\qquad$
$\mathrm{R} / \mathrm{o}$ $\qquad$ , New Delhi

...PETITIONERS

## Versus

1. Union of India through its Standing Counsel Delhi High Court, New Delhi.
2. Land \& Acquisition Collector Delhi Administration, Delhi.
3. Delhi Development Authority, through its Vice Chairman, New Delhi
4. Shri $\qquad$ , Asstt. Director Task Force, DDA, New Delhi 

...RESPONDENTS

## CONTEMPT PETITION UNDER SECTIONS 11, 12 OF THE CONTEMPT OF COURTS ACT, 1971

## MOST RESPECTFULLY SHOWETH:

1. That the President Residents Welfare Association, $\qquad$ New Delhi filed Civil writ Petition No. 2420/2003 in the High Court of Delhi at New Delhi. The respondents in the said petition were the Union of India, Land Acquisition Collector and the DDA. The said petition is still pending and awaiting final disposal.
2. That the Hon'ble court on 1.10 .2003 issued notice to the respondents and granted status quo thereby restraining the respondents including D.D.A. from demolishing the construction raised in the impugned area. The said area included plot No. 1, 2, 3, 4, 21, 22, 35 and 36 belonging to petitioners named above. The above plot were in Khasra No. 78/21/2. The copy of the orders for grant of status quo are annexed herein as Annexures A-1, A-2, A-3, After the issue of Rule on 10.1.2005 (the said order is Annexure A-2) the petition has not come up for hearing.
3. That the petitioners herein the contempt petition have also annexed the site plan. The same is Annexure A-4. The Plot area belonging to the petitioners is marked. Red.
4. The respondent D.D.A. had been conducting demolition in the said area in December/1998 and January, 1999 and since the petitioners apprehended that their property minght also be demolished and therefore, approached the D.D.A. several times and made them aware of the court orders and specially the orders for grant of status quo. A written representation dated 3.12.98 was also routed through the Residents Welfare Association, Vijay Nagar, Phase-I, Delhi to Deputy Director, Land, D.D.A., Delhi.
Annex. A-5 : The copy of the same is annexed as Annexure A-5 alongwith its English Translation. However, despite making the D.D.A. aware of the above/orders of grant of status quo in the Writ Petition (Civil) 2420/2003 the D.D.A. officials namely $\qquad$ alongwith Shri $\qquad$ , came to the site on 4.1.99 at 3.45 P.M. and demolished the construction raised on plot No. 1, Block 'L', Plot No. 2, Block'L', Plot No. 3, Plot No. 4, Plot No. 21, Plot No. 22, Plot No. 35 and 36 belonging to petitioners.

1. That as a result of demolition the petitioners have suffered loss al all the plots had the constructions on it. The details of constructions and the damage incurred is given herein below :
2. That it will not be out of place to mention that the respondent D.D.A. had earlier in the years 2001 and 2002 demolished the construction in the area for which status quo was granted but after the petitioners apprised them of the Court orders they got constructed the building demolished by them at their expense.
3. That the petitioners herein annex as Annexure A-6, the photo graphs of the place where their building situates and have been demolished by the respondent D.D.A.
4. That as detailed above, the petitioners being the owners of plot in Khasra No. 78/21/2 who had been given status quo orders by the Hon'ble Court in Civil Writ Petition 2420/2003 titled Resident Welfare Association v. Union of India and others had every right not to get the construction demolished from the D.D.A. The said status quo is still continuing by virtue of order dated 10.1.2003 of Justice $\qquad$ and Justice $\qquad$ . By not complying with the said status quo orders of the Hon'ble Court, the respondent D.D.A. has committed the contempt of court, It is worthwhile to mentiion that the following officers are the Contemners as they were conducting the demolition. They are Shri $\qquad$ respondent no. $\qquad$ , Shri $\qquad$ respondent no. $\qquad$ and Shri $\qquad$ respondent no. $\qquad$ .
5. The cause of action in the present petition arose when the respondent D.D.A. and specially its officers respondents no. 5, 6, 7, herein were apprised of the status quo orders in Civil Writ Petition 2420/2003 (C.M. No. 3592/2003) and the concerned officers refused to comply with the orders of the court. The cause of action is still continuing as the demolition had already been done on 4.1.2003.

# PRAYER: 

It is therefore most respectfully prayed that the Hon'ble Court may be pleased to initiate contempt proceedings against the above named contemners. It is further prayed that the Hon'ble Court may be pleased to pass such further orders/directions as it may deem fit and proper.

Date:
Place:

Petitioner
Through
Advocate

[Note: The petition must be supported by an affidavit].


# COMPLAINT UNDER OF THE PROTECTION OF WOMEN FROM DOMESTIC VIOLENCE ACT, 2005 

## IN THE COURT OF CHIEF JUDICIAL MAGISTRATE/ CHIEF METROPOLITAN MAGISTRATE <br> COMPLAINT NO. $\qquad$ OF 2017 <br> U/S 12 OF DOMESTIC VIOLENCE ACT

## IN THE MATTER OF :-

Smt. X
W/o Late Sh. Y
R/o $\qquad$

...Complainant

$\qquad$
Sh. Z
S/o
R/o

...Respondent
Police Station:

## COMPLAINT UNDER SECTION 12 OF THE PROTECTION OF WOMEN FROM DOMESTIC VIOLENCE ACT, 2005

Most Respectfully Showeth:

1. That the Respondent is the father- in- law of the Complainant who is harassing and torturing the Petitioner by illegal act of violence in order to throw her out of the matrimonial home.
2. That the Petitioner was married to Late Sh. Y on .....as per Hindu rites and ceremonies and thereafter started living in the matrimonial home as a joint family along with the Respondent and that out of the wedlock following two children were born who are in the care and custody of the complainant. The husband of the complainant died on .....due to illness

| S.No. | Name of <br> Children | Relation | Age | Status |
| :-- | :-- | :-- | :-- | :-- |
| 1 | Master A | Son | 8 | Studying in <br> class IV |
| 2 | Baby B | Daughter | 5 | Studying in <br> class I |

3. That before his death Sh. Y engaged in the manufacturing and trading of Auto parts and was having factory at rented accommodation at $\qquad$ and was running as sole proprietor by the name and style of $\mathrm{M} / \mathrm{s} \ldots .$. and was also running a shop on ground floor.
4. That after the death of the husband of the Complainant on ...the Respondent has misappropriated the machines, tools raw materials etc. lying in the factory of the husband of the complainant and has also trespassed into the shop, belonging to husband of the complainant.
5. That the shop of the husband and Complainant has been taken over by the Respondent who doesn't allow the complainant to enter the same and to run the same.
6. That the Respondent is economically harassing the complainant as he has taken over the shop and doesn't pay any amount to the complainant who has no money and has no earnings at all and is dependent upon the shop of her husband for maintenance
7. That not only this, the Respondent maltreats the complainant in one way or the other and abuses her in filthy language and want her to vacate the second floor of the property so that they may trespass in to the same.
8. That the Respondent threatens the Complainant with the dire consequences on not vacating the second floor of the property.
9. That hence Complainant is left with no other alternative but to file the instant complaint under Section 12 of Protection of Women from Domestic Violence Act as complainant.
10. That the complainant has domestic relationship with the Respondent as Respondent was living with the complainant before the death of her husband.
11. That the deeds and misdeeds of the Respondent are affecting the health and safety of the complainant as well as her two children as after the death of her, the Respondent wants the children to stop going to the school and be sent to an orphanage.
12. That the complaint under Section 12 of the Protection of Women from Domestic Violence Act, 2005 is being filed as such by the aggrieved person.
13. That it is prayed that the Hon'ble court may take cognizance of the complaint and pass all/ any of the orders, as deemed necessary in the circumstances of the case.
14. Orders prayed for are:
I. Protection Order under Section 18 directing Respondent to stay away from Complainant and not to interfere in her possession of the ground floor, second floor of the property in any manner whatsoever
II. Residence Order under Section 19 directing the Respondent to restrain from dispossessing the Complainant from the second and the third floor of property no. .... ( specifically shown in red in site plan enclosed) and to restraint from interfering in the possession of the Complainant on the ground floor of the property including the shop in property no.
III. Monetary Relief under Section 20 directing the Respondent to pay the following expenses as monetary relief
a. Food, clothes, medications and other basic necessities- Rs 15000 p.m.
b. School fees and related expenses - Rs 10000 p.m. amounting to total of Rs 25,000 p.m.
IV. Compensation under Section 22 for causing mental agony and physical suffering by the complainant as deemed fit by this Hon'ble Court.

# PRAYER 

It is, therefore, most respectfully, prayed that this Hon'ble Court be pleased to grant the relief(s) claimed herein and pass such orders as this Hon'ble Court may deem fit and proper under the given facts and circumstances of the case for protecting the Complainant from domestic violence.

Complainant
Through
Advocate

## VERIFICATION

Verified at Delhi on this day of $\qquad$ that the contents of the paras 1 to $\qquad$ of the above complaint are true and correct to my knowledge and nothing material has been concealed there from .

Complainant

- To be accompanied by an affidavit"""


# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAubRNK4o-aJEo2wnCKPVzd9CXMNqUfy3s")
if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY" and not os.environ.get("GEMINI_API_KEY"):
    app.logger.warning("GEMINI_API_KEY is not set. Please replace 'YOUR_GEMINI_API_KEY' in app.py or set the environment variable.")

# --- Gemini API Call Logic (Focusing on genai.Client due to older library version) ---
def call_gemini_api(draft_type_text, instructions_text, supporting_docs_text):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
        raise ValueError("GEMINI_API_KEY is not configured correctly.")

    # Using a generally available model name.
    script_model_to_call = "gemini-1.5-flash-latest"
    # If the above still causes issues, try "gemini-pro" as it's very common.
    # script_model_to_call = "gemini-pro"

    app.logger.info(f"Attempting API call with genai.Client and model: {script_model_to_call}")

    prompt_instruction_text_llm = f"""You are an expert legal drafting assistant specializing in Indian law. Your task is to create accurate and professionally formatted legal documents based on provided templates and user specifications.

Now, please draft the following legal document:

<draft_type>{draft_type_text}</draft_type>

Use the following instructions and context to customize the document:

<instructions>{instructions_text}</instructions>

Additional context and supporting documents:

<supporting_documents>{supporting_docs_text}</supporting_documents>

First, review the comprehensive study material provided:

<study_material>
{study_material}
</study_material>

This study material contains sample drafts and templates for various legal documents, including civil pleadings, matrimonial pleadings, succession act pleadings, constitutional law petitions, criminal law pleadings, and other miscellaneous pleadings.
(Internal Note: The original drafting assistant used a model like "gemini-1.5-flash-preview-0514" for its tasks, but you should act as the expert regardless of internal model details.)

Before drafting the document, please analyze the requirements and explain your approach in your thinking block:
1. Identify appropriate templates from the study material
2. List the key elements from the templates
3. Identify specific information from the instructions and supporting documents that will be used to customize the template
4. Plan out each section of the document, noting where you'll need to use placeholders for missing information
5. Note any areas where you need clarification or additional information

Now, draft the requested legal document. Follow these guidelines:
1. Use appropriate templates from the study material.
2. Incorporate all relevant information from the instructions and supporting documents.
3. Use proper legal language and formatting.
4. Where specific details are missing, use clear placeholders in the format: [Description of PLACEHOLDER]
5. Ensure compliance with Indian legal standards and procedures.
6. Maintain a professional tone throughout the document.

Present your draft in the following format:
<legal_document>
[Insert the drafted legal document here, using appropriate legal formatting, headings, and structure. Use Markdown for rich text elements like headings, lists, bold, italics.]
</legal_document>

After completing the draft, please provide:
<additional_requirements>
1. A list of any information still needed to complete the document
2. Any specific questions about unclear aspects of the instructions
3. Recommendations for additional documentation, if required
</additional_requirements>

Remember to cross-reference with the study material templates, verify legal citations and procedural compliance, and ensure professional presentation and clarity.
Your final output should consist only of the <legal_document> and <additional_requirements> sections and should not duplicate or rehash any of the work you did in the thinking block."""

    contents_for_api = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_instruction_text_llm),
            ],
        ),
    ]
    
    # This matches the user's original Python script's config object name for generate_content_stream
    generate_content_config_obj = types.GenerateContentConfig(
        temperature=0,
        response_mime_type="text/plain",
    )

    full_response_text = ""
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Call as per user's original script structure, using 'config' for the generation settings.
        response_stream = client.models.generate_content_stream(
            model=script_model_to_call,
            contents=contents_for_api,
            config=generate_content_config_obj, # Using 'config' as per original script and error message
        )
        for chunk in response_stream:
            # Accessing text can vary slightly with older SDK versions
            if hasattr(chunk, 'text') and chunk.text is not None:
                full_response_text += chunk.text
            elif hasattr(chunk, 'parts') and chunk.parts:
                for part in chunk.parts:
                    if hasattr(part, 'text') and part.text is not None:
                        full_response_text += part.text
            # Add more specific error handling or logging for chunk structure if needed
            # else:
            #     app.logger.debug(f"Chunk structure not recognized or empty text: {chunk}")

        app.logger.info("Successfully called API using genai.Client structure.")

    except Exception as e:
        app.logger.error(f"API call with `genai.Client` structure failed: {e}", exc_info=True)
        # Since GenerativeModel is not available, this is the only path.
        raise Exception(f"Gemini API call failed: {e}")


    if not full_response_text.strip():
        app.logger.error("Gemini API returned an empty or whitespace-only response.")
        return "Error: Gemini API returned an empty response. Check API key, model name, and logs.", "" # Return tuple
        
    return full_response_text # Return single string

def extract_text_from_pdf(file_stream):
    text = ""
    try:
        reader = PyPDF2.PdfReader(file_stream)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            extracted = page.extract_text()
            if extracted:
                text += extracted
    except Exception as e:
        app.logger.error(f"Error reading PDF: {e}")
        text = f"[Error reading PDF: {e}]"
    return text

def extract_text_from_docx(file_stream):
    text = ""
    try:
        doc = docx.Document(file_stream)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        app.logger.error(f"Error reading DOCX: {e}")
        text = f"[Error reading DOCX: {e}]"
    return text

def parse_gemini_output(raw_output):
    # This function expects raw_output to be a single string
    if not isinstance(raw_output, str): # Defensive check
        app.logger.error(f"parse_gemini_output received non-string input: {type(raw_output)}")
        return "Error: Invalid input to parser.", "Error: Invalid input to parser."

    legal_doc_match = re.search(r"<legal_document>(.*?)</legal_document>", raw_output, re.DOTALL)
    additional_req_match = re.search(r"<additional_requirements>(.*?)</additional_requirements>", raw_output, re.DOTALL)

    legal_document = legal_doc_match.group(1).strip() if legal_doc_match else "Error: Could not parse <legal_document> from response."
    additional_requirements = additional_req_match.group(1).strip() if additional_req_match else "Error: Could not parse <additional_requirements> from response."
    
    if not legal_doc_match and not additional_req_match and raw_output:
        app.logger.warning("Gemini output did not contain expected tags. Raw output provided.")
        legal_document = f"Error or Unexpected Output (tags not found):\n{raw_output}"
        additional_requirements = "Output format was not as expected. See document above."

    return legal_document, additional_requirements

@app.route('/')
def index():
    return render_template('draft_frontend.html')

@app.route('/draft_document', methods=['POST'])
def draft_document_route():
    try:
        draft_type = request.form.get('draft_type')
        instructions = request.form.get('instructions')
        files = request.files.getlist('supporting_documents')

        if not draft_type or not instructions:
            return jsonify({"error": "Draft type and instructions are required."}), 400

        supporting_docs_text = ""
        for file in files:
            if file.filename:
                filename = file.filename.lower()
                file_content_header = f"\n\n--- Content from supporting document: {file.filename} ---\n"
                file_content_footer = "\n--- End of content ---\n"
                extracted_text = ""
                if filename.endswith('.pdf'):
                    extracted_text = extract_text_from_pdf(file.stream)
                elif filename.endswith('.docx'):
                    extracted_text = extract_text_from_docx(file.stream)
                elif filename.endswith('.doc'):
                    extracted_text = "[.doc files are not directly supported for text extraction. Please convert to .docx or .pdf, or paste content into instructions.]"
                
                if extracted_text:
                    supporting_docs_text += file_content_header + extracted_text + file_content_footer

        app.logger.info(f"Calling Gemini for draft type: '{draft_type}'")
        
        # call_gemini_api now returns a single string or raises an exception.
        # If it returns the error tuple, it means the API call itself might have succeeded but returned empty.
        raw_gemini_output_or_error_tuple = call_gemini_api(draft_type, instructions, supporting_docs_text)
        
        # Check if call_gemini_api returned the error tuple (string, string)
        if isinstance(raw_gemini_output_or_error_tuple, tuple) and len(raw_gemini_output_or_error_tuple) == 2:
            # This case handles the "API returned empty response" scenario within call_gemini_api
            legal_document, additional_requirements = raw_gemini_output_or_error_tuple
        elif isinstance(raw_gemini_output_or_error_tuple, str):
            legal_document, additional_requirements = parse_gemini_output(raw_gemini_output_or_error_tuple)
        else:
            # Should not happen if call_gemini_api is correctly implemented
            app.logger.error("Unexpected return type from call_gemini_api")
            raise Exception("Internal error: Unexpected response from API handling.")


        return jsonify({
            "legal_document": legal_document,
            "additional_requirements": additional_requirements
        })

    except ValueError as ve: 
        app.logger.error(f"Configuration error: {ve}")
        return jsonify({"error": str(ve)}), 500
    except Exception as e:
        app.logger.error(f"An error occurred in /draft_document: {e}", exc_info=True)
        # Ensure the error message passed to jsonify is a string.
        error_message = str(e) if e else "An unknown internal server error occurred."
        return jsonify({"error": f"An internal server error occurred: {error_message}"}), 500


if __name__ == '__main__':
    if not os.path.exists("templates"):
        os.makedirs("templates")
    if not os.path.exists("templates/draft_frontend.html"):
        with open("templates/draft_frontend.html", "w") as f:
            f.write("<html><body><h1>Loading app...</h1><p>If you see this, ensure your main index.html is correctly placed in the 'templates' folder.</p></body></html>")
            
    app.run(debug=True, host='0.0.0.0', port=5000)