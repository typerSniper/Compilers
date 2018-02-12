
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'DTYPE EQUALS LPAREN RPAREN LCPAREN RCPAREN RETTYPE FUNCNAME SEMICOL COMMA AMP WORD REF NUMBER PLUS MINUS DIVexpression : RETTYPE FUNCNAME LPAREN RPAREN LCPAREN BODY RCPAREN\n\tBODY : DECL SEMICOL BODY \n\t\t\t| ASSIGN SEMICOL BODY\n\t\t\t| \n\t\n\tDECL : DTYPE DECLIST\n\t\n\tDECLIST : ID COMMA DECLIST \n\t\t\t| ID\n\t\n\tID : WORD\n\t   | REF ID\n\t\n\tLHS_POINT : REF aID\n\t\n\tASSIGN : PRIM\n\t\n\tPRIM : WORD EQUALS Wrhs\n\t\t| LHS_POINT EQUALS Wrhs\n\t\t| LHS_POINT EQUALS Nrhs\n\t\n\taID : WORD\n\t\t| AMP aID\n\t\t| REF aID\n\t\n\tRWatom : aID\n\t\t  | MINUS RWatom\n\t\n\tNatom : NUMBER\n\t\t  | MINUS Natom\n\t\n\t\tWrhs : RWatom \n\t\t\t | Wrhs PLUS RWatom\n\t\t\t | Wrhs MINUS RWatom\n\t\t\t | Wrhs REF RWatom\n\t\t\t | Wrhs DIV RWatom\n\t\t\t | Wrhs PLUS Nrhs\n\t\t\t | Wrhs MINUS Nrhs\n\t\t\t | Wrhs REF Nrhs\n\t\t\t | Wrhs DIV Nrhs\n\t\t\t | Nrhs PLUS Wrhs\n\t\t\t | Nrhs MINUS Wrhs\n\t\t\t | Nrhs REF Wrhs\n\t\t\t | Nrhs DIV Wrhs\n\t\t\t | LPAREN Wrhs RPAREN\n\t\n\t\tNrhs : Natom \n\t\t\t | Nrhs PLUS Natom\n\t\t\t | Nrhs MINUS Natom\n\t\t\t | Nrhs REF Natom\n\t\t\t | Nrhs DIV Natom\n\t\t\t | LPAREN Nrhs RPAREN\n\t'
    
_lr_action_items = {'NUMBER':([21,22,33,38,47,48,49,50,51,52,53,54,59,70,78,79,80,81,82,],[31,31,31,31,31,31,31,31,31,31,31,31,31,31,31,31,31,31,31,]),'EQUALS':([11,12,24,26,42,43,],[21,22,-15,-10,-16,-17,]),'MINUS':([21,22,24,31,32,33,34,35,36,37,38,39,40,42,43,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,],[38,38,-15,-20,-18,38,48,52,-22,-36,38,48,52,-16,-17,48,52,38,38,38,38,70,70,70,70,-21,-19,-35,-41,78,80,-23,80,-24,80,-26,80,-25,48,-36,70,48,-36,48,-36,48,-36,80,78,78,78,78,78,-37,-38,-40,-39,]),'RETTYPE':([0,],[2,]),'LPAREN':([3,21,22,33,47,48,49,50,51,52,53,54,59,],[4,33,33,33,59,59,59,59,33,33,33,33,59,]),'DTYPE':([6,16,23,],[9,9,9,]),'DIV':([24,31,32,34,35,36,37,39,40,42,43,45,46,55,56,57,58,60,61,62,63,64,65,66,67,68,69,71,72,73,74,75,76,77,83,84,85,86,],[-15,-20,-18,49,53,-22,-36,49,53,-16,-17,49,53,-21,-19,-35,-41,81,-23,81,-24,81,-26,81,-25,49,-36,49,-36,49,-36,49,-36,81,-37,-38,-40,-39,]),'WORD':([6,9,14,16,17,21,22,23,25,27,30,33,38,47,48,49,50,51,52,53,54,70,],[12,19,24,12,19,24,24,12,24,24,19,24,24,24,24,24,24,24,24,24,24,24,]),'RCPAREN':([6,7,16,23,28,41,],[-4,15,-4,-4,-2,-3,]),'COMMA':([19,20,29,],[-8,30,-9,]),'FUNCNAME':([2,],[3,]),'SEMICOL':([8,10,13,18,19,20,24,29,31,32,34,35,36,37,39,42,43,44,55,56,57,58,60,61,62,63,64,65,66,67,68,69,71,72,73,74,75,76,83,84,85,86,],[16,-11,23,-5,-8,-7,-15,-9,-20,-18,-13,-14,-22,-36,-12,-16,-17,-6,-21,-19,-35,-41,-27,-23,-28,-24,-30,-26,-29,-25,-31,-37,-32,-38,-34,-40,-33,-39,-37,-38,-40,-39,]),'PLUS':([24,31,32,34,35,36,37,39,40,42,43,45,46,55,56,57,58,60,61,62,63,64,65,66,67,68,69,71,72,73,74,75,76,77,83,84,85,86,],[-15,-20,-18,47,51,-22,-36,47,51,-16,-17,47,51,-21,-19,-35,-41,79,-23,79,-24,79,-26,79,-25,47,-36,47,-36,47,-36,47,-36,79,-37,-38,-40,-39,]),'RPAREN':([4,24,31,32,36,37,42,43,45,46,55,56,57,58,60,61,62,63,64,65,66,67,68,69,71,72,73,74,75,76,77,83,84,85,86,],[5,-15,-20,-18,-22,-36,-16,-17,57,58,-21,-19,-35,-41,-27,-23,-28,-24,-30,-26,-29,-25,-31,-37,-32,-38,-34,-40,-33,-39,58,-37,-38,-40,-39,]),'$end':([1,15,],[0,-1,]),'LCPAREN':([5,],[6,]),'AMP':([14,21,22,25,27,33,38,47,48,49,50,51,52,53,54,70,],[25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,25,]),'REF':([6,9,14,16,17,21,22,23,24,25,27,30,31,32,33,34,35,36,37,38,39,40,42,43,45,46,47,48,49,50,51,52,53,54,55,56,57,58,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,83,84,85,86,],[14,17,27,14,17,27,27,14,-15,27,27,17,-20,-18,27,50,54,-22,-36,27,50,54,-16,-17,50,54,27,27,27,27,27,27,27,27,-21,-19,-35,-41,82,-23,82,-24,82,-26,82,-25,50,-36,27,50,-36,50,-36,50,-36,82,-37,-38,-40,-39,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'BODY':([6,16,23,],[7,28,41,]),'LHS_POINT':([6,16,23,],[11,11,11,]),'Natom':([21,22,33,38,47,48,49,50,51,52,53,54,59,70,78,79,80,81,82,],[37,37,37,55,37,37,37,37,69,72,74,76,37,55,55,83,84,85,86,]),'DECL':([6,16,23,],[8,8,8,]),'ASSIGN':([6,16,23,],[13,13,13,]),'expression':([0,],[1,]),'ID':([9,17,30,],[20,29,20,]),'Wrhs':([21,22,33,51,52,53,54,],[34,39,45,68,71,73,75,]),'Nrhs':([21,22,33,47,48,49,50,51,52,53,54,59,],[35,40,46,60,62,64,66,40,40,40,40,77,]),'aID':([14,21,22,25,27,33,38,47,48,49,50,51,52,53,54,70,],[26,32,32,42,43,32,32,32,32,32,32,32,32,32,32,32,]),'RWatom':([21,22,33,38,47,48,49,50,51,52,53,54,70,],[36,36,36,56,61,63,65,67,36,36,36,36,56,]),'DECLIST':([9,30,],[18,44,]),'PRIM':([6,16,23,],[10,10,10,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> RETTYPE FUNCNAME LPAREN RPAREN LCPAREN BODY RCPAREN','expression',7,'p_expression_prog','parser.py',79),
  ('BODY -> DECL SEMICOL BODY','BODY',3,'p_expression_body','parser.py',82),
  ('BODY -> ASSIGN SEMICOL BODY','BODY',3,'p_expression_body','parser.py',83),
  ('BODY -> <empty>','BODY',0,'p_expression_body','parser.py',84),
  ('DECL -> DTYPE DECLIST','DECL',2,'p_expression_decl','parser.py',88),
  ('DECLIST -> ID COMMA DECLIST','DECLIST',3,'p_expression_declist','parser.py',101),
  ('DECLIST -> ID','DECLIST',1,'p_expression_declist','parser.py',102),
  ('ID -> WORD','ID',1,'p_expression_id','parser.py',108),
  ('ID -> REF ID','ID',2,'p_expression_id','parser.py',109),
  ('LHS_POINT -> REF aID','LHS_POINT',2,'p_expression_lhspointer','parser.py',122),
  ('ASSIGN -> PRIM','ASSIGN',1,'p_expression_assign','parser.py',126),
  ('PRIM -> WORD EQUALS Wrhs','PRIM',3,'p_prim','parser.py',131),
  ('PRIM -> LHS_POINT EQUALS Wrhs','PRIM',3,'p_prim','parser.py',132),
  ('PRIM -> LHS_POINT EQUALS Nrhs','PRIM',3,'p_prim','parser.py',133),
  ('aID -> WORD','aID',1,'p_expression_assignId','parser.py',140),
  ('aID -> AMP aID','aID',2,'p_expression_assignId','parser.py',141),
  ('aID -> REF aID','aID',2,'p_expression_assignId','parser.py',142),
  ('RWatom -> aID','RWatom',1,'p_expression_RWatom','parser.py',164),
  ('RWatom -> MINUS RWatom','RWatom',2,'p_expression_RWatom','parser.py',165),
  ('Natom -> NUMBER','Natom',1,'p_expression_Natom','parser.py',169),
  ('Natom -> MINUS Natom','Natom',2,'p_expression_Natom','parser.py',170),
  ('Wrhs -> RWatom','Wrhs',1,'p_expression_Wrhs','parser.py',175),
  ('Wrhs -> Wrhs PLUS RWatom','Wrhs',3,'p_expression_Wrhs','parser.py',176),
  ('Wrhs -> Wrhs MINUS RWatom','Wrhs',3,'p_expression_Wrhs','parser.py',177),
  ('Wrhs -> Wrhs REF RWatom','Wrhs',3,'p_expression_Wrhs','parser.py',178),
  ('Wrhs -> Wrhs DIV RWatom','Wrhs',3,'p_expression_Wrhs','parser.py',179),
  ('Wrhs -> Wrhs PLUS Nrhs','Wrhs',3,'p_expression_Wrhs','parser.py',180),
  ('Wrhs -> Wrhs MINUS Nrhs','Wrhs',3,'p_expression_Wrhs','parser.py',181),
  ('Wrhs -> Wrhs REF Nrhs','Wrhs',3,'p_expression_Wrhs','parser.py',182),
  ('Wrhs -> Wrhs DIV Nrhs','Wrhs',3,'p_expression_Wrhs','parser.py',183),
  ('Wrhs -> Nrhs PLUS Wrhs','Wrhs',3,'p_expression_Wrhs','parser.py',184),
  ('Wrhs -> Nrhs MINUS Wrhs','Wrhs',3,'p_expression_Wrhs','parser.py',185),
  ('Wrhs -> Nrhs REF Wrhs','Wrhs',3,'p_expression_Wrhs','parser.py',186),
  ('Wrhs -> Nrhs DIV Wrhs','Wrhs',3,'p_expression_Wrhs','parser.py',187),
  ('Wrhs -> LPAREN Wrhs RPAREN','Wrhs',3,'p_expression_Wrhs','parser.py',188),
  ('Nrhs -> Natom','Nrhs',1,'p_expression_Nrhs','parser.py',193),
  ('Nrhs -> Nrhs PLUS Natom','Nrhs',3,'p_expression_Nrhs','parser.py',194),
  ('Nrhs -> Nrhs MINUS Natom','Nrhs',3,'p_expression_Nrhs','parser.py',195),
  ('Nrhs -> Nrhs REF Natom','Nrhs',3,'p_expression_Nrhs','parser.py',196),
  ('Nrhs -> Nrhs DIV Natom','Nrhs',3,'p_expression_Nrhs','parser.py',197),
  ('Nrhs -> LPAREN Nrhs RPAREN','Nrhs',3,'p_expression_Nrhs','parser.py',198),
]
