import random

# Tabela de Harmonia de Cores
COMBINACOES_CORES = {
    'preto': ['branco', 'cinza', 'jeans', 'vermelho', 'rosa', 'azul', 'amarelo', 'verde', 'bege'],
    'branco': ['preto', 'cinza', 'jeans', 'rosa', 'azul', 'verde', 'vermelho', 'bege'],
    'cinza': ['preto', 'branco', 'rosa', 'azul', 'vermelho', 'jeans'],
    'jeans': ['preto', 'branco', 'cinza', 'rosa', 'vermelho', 'amarelo', 'verde'],
    'azul': ['preto', 'branco', 'cinza', 'jeans', 'bege'],
    'rosa': ['preto', 'branco', 'cinza', 'jeans'],
    'bege': ['preto', 'branco', 'azul', 'verde', 'vermelho'],
    'vermelho': ['preto', 'branco', 'cinza', 'jeans'],
    'verde': ['preto', 'branco', 'jeans', 'bege'],
}

# Compatibilidade entre Estilos
COMPATIBILIDADE_ESTILOS = {
    'casual': ['casual', 'esporte', 'festa'],
    'formal': ['formal', 'trabalho'],
    'trabalho': ['trabalho', 'formal', 'casual'],
    'festa': ['festa', 'casual'],
    'esporte': ['esporte', 'casual']
}


def sao_estilos_compativeis(estilo1, estilo2):
    """Verifica se dois estilos combinam entre si."""
    e1 = estilo1.lower().strip() if estilo1 else 'casual'
    e2 = estilo2.lower().strip() if estilo2 else 'casual'

    if e1 == e2:
        return True

    comp1 = COMPATIBILIDADE_ESTILOS.get(e1, ['casual'])
    return e2 in comp1


def sao_cores_harmonicas(cor1, cor2):
    """Verifica se duas cores combinam segundo a tabela de harmonia."""
    c1 = cor1.lower().strip()
    c2 = cor2.lower().strip()

    if c1 == c2:
        return True

    combinacoes = COMBINACOES_CORES.get(c1, [])
    return c2 in combinacoes


def gerar_recomendacao_look(pecas, clima='Geral', ocasiao='Geral'):
    """
    Algoritmo de recomendação inteligente que considera:
    - Categoria da peça (superior x inferior)
    - Clima/Temperatura
    - Harmonia de Cores
    - Compatibilidade de Estilo
    """
    # 1. Separar as peças por categoria superior e inferior
    categorias_superiores = ['camiseta', 'blusa', 'camisa', 'casaco', 'jaqueta', 'top', 'moletom']
    categorias_inferiores = ['calça', 'short', 'bermuda', 'saia', 'calca']

    pecas_superiores = [p for p in pecas if p.categoria.lower().strip() in categorias_superiores]
    pecas_inferiores = [p for p in pecas if p.categoria.lower().strip() in categorias_inferiores]

    # Se não houver peças suficientes das duas categorias
    if not pecas_superiores or not pecas_inferiores:
        return None, "É necessário ter pelo menos uma peça superior e uma inferior cadastradas."

    # 2. Filtrar por clima se especificado
    if clima.lower() == 'verão':
        pecas_superiores = [p for p in pecas_superiores if
                            p.categoria.lower().strip() not in ['casaco', 'jaqueta', 'moletom']]
        pecas_inferiores = [p for p in pecas_inferiores if
                            p.categoria.lower().strip() in ['short', 'bermuda', 'saia']] or pecas_inferiores
    elif clima.lower() == 'inverno':
        pecas_inferiores = [p for p in pecas_inferiores if
                            p.categoria.lower().strip() not in ['short', 'bermuda']] or pecas_inferiores

    # 3. Buscar par ideal combinando cor e estilo
    combinacoes_validas = []

    for sup in pecas_superiores:
        for inf in pecas_inferiores:
            cor_combina = sao_cores_harmonicas(sup.cor, inf.cor)
            estilo_combina = sao_estilos_compativeis(getattr(sup, 'estilo', ''), getattr(inf, 'estilo', ''))

            # Dá peso maior para pares que combinam cor AND estilo
            if cor_combina and estilo_combina:
                combinacoes_validas.append((sup, inf, "perfeita"))
            elif cor_combina:
                combinacoes_validas.append((sup, inf, "boa_cor"))
            elif estilo_combina:
                combinacoes_validas.append((sup, inf, "bom_estilo"))

    # 4. Selecionar o melhor par
    if combinacoes_validas:
        # Prioriza combinações perfeitas (cor + estilo)
        perfeitas = [pair for pair in combinacoes_validas if pair[2] == "perfeita"]
        if perfeitas:
            sup, inf, tipo = random.choice(perfeitas)
            descricao = (f"Look perfeito! A {sup.categoria} ({sup.cor}, estilo {sup.estilo or 'casual'}) "
                         f"harmoniza em cores e estilo com a {inf.categoria} ({inf.cor}, estilo {inf.estilo or 'casual'}).")
        else:
            sup, inf, tipo = random.choice(combinacoes_validas)
            descricao = (f"Sugestão de look: {sup.categoria} ({sup.cor}) combinada com {inf.categoria} ({inf.cor}).")
    else:
        # Fallback inteligente
        sup = random.choice(pecas_superiores)
        inf = random.choice(pecas_inferiores)
        descricao = f"Combinação casual: {sup.categoria} ({sup.cor}) com {inf.categoria} ({inf.cor})."

    nome_look = f"Look {clima.capitalize()} - {sup.categoria.capitalize()} & {inf.categoria.capitalize()}"
    return (sup, inf), descricao, nome_look