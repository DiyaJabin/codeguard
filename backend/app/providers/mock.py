import re
from uuid import uuid4
class MockReviewProvider:
    name="mock-demo"
    def analyze(self,code,language):
        fs=[]; lines=code.splitlines()
        def add(title,cat,sev,desc,line,rec): fs.append({"finding_id":str(uuid4()),"title":title,"category":cat,"severity":sev,"description":desc,"affected_lines":[line],"recommendation":rec,"suggested_code":"","confidence":0.94})
        for i,line in enumerate(lines,1):
            low=line.lower()
            if re.search(r"(password|api[_-]?key|secret|token)\s*[:=]",low): add("Hardcoded credential pattern","Security","High","A credential-like value may be exposed.",i,"Load secrets from environment variables or a managed secret store.")
            if language=="Python" and re.search(r"except\s*:\s*$",line): add("Bare except block","Reliability","Medium","A bare except catches unrelated errors.",i,"Catch the narrow exception types you expect.")
            if language=="Python" and re.search(r"def\s+\w+\([^)]*=\s*(\[|\{|set\()",line): add("Mutable default argument","Maintainability","High","Mutable defaults persist between calls.",i,"Use None and initialize inside the function.")
            if language=="Java" and re.search(r"catch\s*\([^)]*\)\s*\{\s*\}",line): add("Empty catch block","Reliability","Medium","The exception is swallowed without recovery.",i,"Log the exception or recover deliberately.")
        if language=="Java" and "System.out.println" in code: add("Direct console output","Maintainability","Low","Use configurable logging in production.",next(i for i,x in enumerate(lines,1) if "System.out.println" in x),"Use a structured logger.")
        sev={s:sum(f["severity"]==s for f in fs) for s in ["Critical","High","Medium","Low","Informational"]}; cats={}
        for f in fs: cats[f["category"]]=cats.get(f["category"],0)+1
        return {"analysis_provider":self.name,"summary":f"Demo analysis identified {len(fs)} potential improvement(s) in this {language} snippet.","total_issues":len(fs),"severity_counts":sev,"category_counts":cats,"findings":fs}
