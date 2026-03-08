# LeetCode_Problem
Problema 1 — Clone Graph
O que o problema pede
Dado um nó de um grafo, precisamos fazer uma cópia completa do grafo inteiro. Não uma cópia rasa que ainda aponta pros nós originais uma copia de verdade, onde cada nó e um objeto novo na memória.

Diferença entre Shallow Copy e Deep Copy
Antes de sair “codando”, entendemos que precisávamos ter clareza sobre isso:

Shallow Copy (cópia rasa):
•	original e clone apontam pro mesmo objeto na memória
•	mexer em um afeta o outro,  não é isso que queremos

Deep Copy (cópia profunda):
•	cada nó é um objeto completamente novo e independente
•	podemos mexer em qualquer um sem afetar o original

Por que grafos complicam a cópia
Grafos podem ter ciclos, nós que apontam uns para os outros. Sem controle, a recursão entra em loop infinito:

Grafo:  1 — 2 — 3 — 4 — 1  (ciclo!)

Sem controle:
  clonar(1) → clonar(2) → clonar(1) → clonar(2) → ... trava

A solucão: HashMap como registro de clones
Usamos um HashMap para guardar todos os clones já criados. Antes de clonar qualquer nó, verificamos se já existe uma cópia dele nesse registro. Se existir, devolvo essa cópia e paramos a recursão ali. Se não existir, crio um clone novo e continuo.

visitados = {
    Node(1): Clone(1),
    Node(2): Clone(2),
}

A ordem de registro e critica
O clone precisa ser registrado no HashMap antes de visitar os vizinhos. Descobrimos que se fizer depois, ciclos ainda causam loop infinito porque o nó já foi visitado, mas ainda não está no registro:

Errado: registra depois dos vizinhos:
clone = Node(no.val)
for vizinho in no.neighbors:
    clone.neighbors.append(dfs(vizinho))
visitados[no] = clone

Correto: registra antes dos vizinhos:
clone = Node(no.val)
visitados[no] = clone
for vizinho in no.neighbors:
    clone.neighbors.append(dfs(vizinho))
Código completo

    class Solution:  
	
	  def cloneGraph(self, node):
        
		 if not node:
           
			return None

         visitados = {}

         def dfs(no):
            if no in visitados:
                return visitados[no]

            clone = Node(no.val)
            visitados[no] = clone

            for vizinho in no.neighbors:
                clone.neighbors.append(dfs(vizinho))

            return clone

         return dfs(node)

Complexidade

 
	Complexidade	Motivo
Tempo	O(V + E)	Visita cada no e aresta uma única vez
Espaço	O(V)	HashMap armazena um clone por no

 
Problema 2 — Course Schedule
O que o problema pede
Temos N cursos numerados de 0 a N-1 e uma lista de pré-requisitos. Cada par [a, b] significa que precisamos fazer o curso b antes do curso a. O objetivo e descobrir se é possível completar todos os cursos.

Por que um ciclo torna isso impossível
Se existe uma dependência circular nos pré-requisitos, não há ordem válida para começar , é um travamento logico sem saída:

prerequisites = [[1,0],[0,1]]

Para fazer o curso 0, preciso do curso 1.
Para fazer o curso 1, preciso do curso 0.
Nunca termina. Impossível.

O coração da solução: 3 estados por no
Cada nó recebe um estado que representa o que sabemos sobre ele naquele momento da execução:

Estado 0 — ainda não visitamos
O nó ainda não foi processado. Precisa entrar na pilha de recursão.

Estado 1 — estamos visitando agora
O nó está na pilha de recursão ativa no momento. Se durante a recursão eu encontrar de novo um nó com estado 1, significa que voltamos a ele pelo mesmo caminho, isso é um ciclo e retorna False imediatamente.

caminho:  0 → 1 → 2 → 0
                       ↑
                    estado 1, ciclo detectado

Estado 2 — já terminamos de verificar
Já processamos esse nó completamente e provamos que não tem ciclo saindo dele. Se ele aparecer de novo em outra ramificação, podemos ignorar com segurança e retornar True.

Por que 2 estados não bastam
Com apenas visitado e não-visitado, quando dois caminhos diferentes chegam no mesmo nó, o segundo caminho vê o nó como visitado e gera um falso positivo de ciclo. O estado 2 resolve isso ao distinguir um nó que está sendo visitado agora de um nó que já foi totalmente verificado:

Grafo:  0 → 2
        1 → 2

Com 2 estados:
  dfs(0) visita 2, marca visitado
  dfs(1) visita 2, ja marcado → falso positivo de ciclo

Com 3 estados:
  dfs(0) visita 2, marca estado 2
  dfs(1) visita 2, estado 2 → seguro, continua

Código completo

    class Solution:
   
	 def canFinish(self, numCourses, prerequisites):
       
		grafo = {i: [] for i in range(numCourses)}
       
		for curso, pre in prerequisites:
           
			grafo[curso].append(pre)

        estado = [0] * numCourses

        def dfs(curso):
            if estado[curso] == 1:
                return False
            if estado[curso] == 2:
                return True

            estado[curso] = 1

            for vizinho in grafo[curso]:
                if not dfs(vizinho):
                    return False

            estado[curso] = 2
            return True

        for curso in range(numCourses):
            if not dfs(curso):
                return False

        return True

    Complexidade

	Complexidade	Motivo
    Tempo	O(V + E)	Cada curso e pre-requisito e visitado uma vez
    Espaco	O(V + E)	Grafo de adjacencia +  array de estados + pilha de recursao

 
Comparando os dois

	Clone Graph	Course Schedule
    Objetivo	Copiar o grafo inteiro	Detectar se há ciclo
    Ciclo	Problema a evitar	A resposta do problema
    Controle de visitados	HashMap: no → clone	Array de 3 estados [0, 1, 2]
    Quando para a recursão	No já no HashMap	Estado 1 (ciclo) ou Estado 2 (seguro)
    Retorno	Novo no clonado	True ou False
    Complexidade Tempo	O(V + E)	O(V + E)
    Complexidade Espaço	O(V)	O(V + E)


O padrão que os dois compartilham
Apesar de resolverem coisas diferentes, os dois seguem o mesmo esquema de DFS: verificamos se já processei o nó, marco que estamos processando agora, processamos o nó, fazemos a recursão nos vizinhos e finalizamos atualizando o estado.

No fundo, os dois são lados da mesma moeda. No Clone Graph usamos o HashMap pra construir algo novo. No Course Schedule usamos os 3 estados pra detectar um problema. A estrutura do DFS é idêntica nos dois, o que muda é só o que fazemos com a informação.
