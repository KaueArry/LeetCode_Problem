import requests
from collections import defaultdict

GITHUB_TOKEN = "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"

HEADERS = {}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


# Busca de dados da API do GitHub 
def buscar_seguidores(usuario: str, limite: int = 10) -> list[str]:
    url = f"https://api.github.com/users/{usuario}/followers?per_page={limite}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"  Erro ao buscar seguidores de {usuario}: {response.status_code}")
        return []
    return [u["login"] for u in response.json()]


def buscar_seguindo(usuario: str, limite: int = 10) -> list[str]:
    url = f"https://api.github.com/users/{usuario}/following?per_page={limite}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"  Erro ao buscar seguindo de {usuario}: {response.status_code}")
        return []
    return [u["login"] for u in response.json()]


def construir_grafo_github(usuario_inicial: str, profundidade: int = 2, limite_por_no: int = 5) -> dict:
    """
    Constroi um grafo direcionado a partir de um usuario do GitHub.
    Uma aresta A → B significa que A segue B.
    Profundidade controla quantos niveis de seguidores buscar.
    """
    print(f"\nConstruindo grafo a partir de '{usuario_inicial}'...")
    grafo = defaultdict(list)
    visitados = set()
    fila = [(usuario_inicial, 0)]

    while fila:
        usuario, nivel = fila.pop(0)

        if usuario in visitados or nivel > profundidade:
            continue
        visitados.add(usuario)

        print(f"  Buscando conexoes de: {usuario} (nivel {nivel})")
        seguidores = buscar_seguidores(usuario, limite=limite_por_no)

        grafo[usuario] = seguidores

        for outro in seguidores:
            if outro not in visitados:
                fila.append((outro, nivel + 1))

    print(f"\nGrafo construido: {len(grafo)} nos, {sum(len(v) for v in grafo.values())} arestas\n")
    return dict(grafo)


# Algoritmo DFS com 3 estados (Course Schedule)
def detectar_ciclos(grafo: dict) -> dict:
    """
    Aplica DFS com 3 estados para detectar ciclos na rede de seguidores.

    Estado 0 — nao visitado
    Estado 1 — visitando agora (esta na pilha de recursao)
    Estado 2 — concluido e seguro

    Se encontrar um no com estado 1 durante a recursao, ha um ciclo:
    significa que usuario A segue B, B segue C, e C segue A de volta.
    """
    todos_nos = set(grafo.keys())
    for vizinhos in grafo.values():
        todos_nos.update(vizinhos)

    estado = {no: 0 for no in todos_nos}
    ciclos_encontrados = []
    caminho_atual = []

    def dfs(no):
        if estado[no] == 1:
            # Ciclo detectado — registra o trecho do ciclo
            idx = caminho_atual.index(no)
            ciclo = caminho_atual[idx:] + [no]
            ciclos_encontrados.append(ciclo)
            return True

        if estado[no] == 2:
            return False

        estado[no] = 1
        caminho_atual.append(no)

        for vizinho in grafo.get(no, []):
            dfs(vizinho)

        caminho_atual.pop()
        estado[no] = 2
        return False

    for no in todos_nos:
        if estado[no] == 0:
            dfs(no)

    return {
        "total_nos": len(todos_nos),
        "ciclos_encontrados": ciclos_encontrados,
        "tem_ciclo": len(ciclos_encontrados) > 0
    }


def grau_de_separacao(grafo: dict, origem: str, destino: str) -> dict:
    """
    Usa o mesmo DFS com rastreamento de caminho para encontrar
    se existe um caminho de 'origem' ate 'destino' na rede.
    Retorna o caminho e o grau de separacao.
    """
    todos_nos = set(grafo.keys())
    for vizinhos in grafo.values():
        todos_nos.update(vizinhos)

    if origem not in todos_nos:
        return {"encontrado": False, "motivo": f"Usuario '{origem}' nao esta no grafo"}
    if destino not in todos_nos:
        return {"encontrado": False, "motivo": f"Usuario '{destino}' nao esta no grafo"}

    estado = {no: 0 for no in todos_nos}
    caminho_encontrado = []

    def dfs(no, caminho):
        if estado[no] == 1 or estado[no] == 2:
            return False

        estado[no] = 1
        caminho.append(no)

        if no == destino:
            caminho_encontrado.extend(caminho)
            return True

        for vizinho in grafo.get(no, []):
            if dfs(vizinho, caminho):
                return True

        caminho.pop()
        estado[no] = 2
        return False

    encontrou = dfs(origem, [])

    if encontrou:
        return {
            "encontrado": True,
            "origem": origem,
            "destino": destino,
            "grau_de_separacao": len(caminho_encontrado) - 1,
            "caminho": caminho_encontrado
        }
    return {
        "encontrado": False,
        "motivo": f"Nao ha caminho de '{origem}' ate '{destino}' na rede mapeada"
    }


def influenciadores(grafo: dict, top_n: int = 5) -> list:
    """
    Identifica os nos mais referenciados no grafo
    ou seja, os desenvolvedores mais seguidos dentro da rede mapeada.
    """
    contagem = defaultdict(int)
    for vizinhos in grafo.values():
        for v in vizinhos:
            contagem[v] += 1

    ranking = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
    return [{"usuario": u, "seguido_por": n} for u, n in ranking[:top_n]]


# Execucao principal 
if __name__ == "__main__":
    USUARIO_INICIAL = "Google"   # ponto de entrada na rede
    PROFUNDIDADE    = 2            # quantos niveis de conexoes buscar
    LIMITE_POR_NO   = 5            # quantos seguindo buscar por usuario

    # 1. Constroi o grafo consumindo a API do GitHub
    grafo = construir_grafo_github(
        usuario_inicial=USUARIO_INICIAL,
        profundidade=PROFUNDIDADE,
        limite_por_no=LIMITE_POR_NO
    )

    # 2. Detecta ciclos com DFS de 3 estados (Course Schedule)
    print("=" * 55)
    print("DETECCAO DE CICLOS — DFS com 3 estados")
    print("=" * 55)
    resultado_ciclos = detectar_ciclos(grafo)
    print(f"Total de nos no grafo : {resultado_ciclos['total_nos']}")
    print(f"Ciclos encontrados    : {len(resultado_ciclos['ciclos_encontrados'])}")

    if resultado_ciclos["tem_ciclo"]:
        print("\nExemplos de ciclos (A segue B, B segue ... segue A):")
        for ciclo in resultado_ciclos["ciclos_encontrados"][:3]:
            print(f"  {' → '.join(ciclo)}")
    else:
        print("Nenhum ciclo encontrado na rede mapeada.")

    # 3. Grau de separacao entre dois desenvolvedores
    print("\n" + "=" * 55)
    print("GRAU DE SEPARACAO")
    print("=" * 55)

    nos_disponiveis = list(grafo.keys())
    if len(nos_disponiveis) >= 2:
        origem  = nos_disponiveis[0]
        destino = nos_disponiveis[-1]
        resultado_sep = grau_de_separacao(grafo, origem, destino)

        if resultado_sep["encontrado"]:
            print(f"De '{origem}' ate '{destino}':")
            print(f"  Grau de separacao : {resultado_sep['grau_de_separacao']}")
            print(f"  Caminho           : {' → '.join(resultado_sep['caminho'])}")
        else:
            print(resultado_sep["motivo"])

    # 4. Desenvolvedores mais influentes na rede
    print("\n" + "=" * 55)
    print("TOP INFLUENCIADORES DA REDE")
    print("=" * 55)
    top = influenciadores(grafo, top_n=5)
    for i, dev in enumerate(top, 1):
        print(f"  {i}. {dev['usuario']:20s} seguido por {dev['seguido_por']} nos da rede")

