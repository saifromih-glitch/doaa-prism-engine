ALLOWED={("proposal","gate"),("gate","human_review"),("human_review","approved"),("approved","separate_ready")}

def verify_transition(current_state, next_state):
    if not isinstance(current_state,str) or not isinstance(next_state,str):
        return {"status":"transition_blocked","reason":"state_invalid","execution_authority":"none","automatic_execution":False}
    if (current_state,next_state) not in ALLOWED:
        return {"status":"transition_blocked","reason":"transition_not_allowed","execution_authority":"none","automatic_execution":False}
    return {"status":"transition_verified","from_state":current_state,"to_state":next_state,"execution_authority":"none","automatic_execution":False,"safe":True}

