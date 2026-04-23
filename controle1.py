Culto=input("Digite o nome do culto: ")     
Data=input("Digite a data do culto (dd/mm/aaaa): ")
dias_semana=["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
dia_semana=input("Digite o dia da semana: ")
menina=int(input("Digite o total de meninas: "))
print(f"Total de meninas: {menina}")
menino=int(input("Digite o total de meninos: "))
print(f"Total de meninos: {menino}")
visitante=int(input("Digite o total de visitantes: "))
print(f"Total de visitantes: {visitante}")
Tios=int(input("Digite o total de tios: "))
print(f"Total de tios: {Tios}")
total=menina+menino+visitante+Tios
print(f"Total geral de presentes: {total}")


