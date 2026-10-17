import random

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

COMPATIBILIDADE_ESTILOS = {
    'casual': ['casual', 'esporte', 'festa'],
    'formal': ['formal', 'trabalho'],
    'trabalho': ['trabalho', 'formal', 'casual'],
    'festa': ['festa', 'casual'],
    'esporte': ['esporte', 'casual']
}


def sao_estilos_compativeis(estilo1, estilo2):
    e1 = estilo1.lower().strip() if estilo1 else 'casual'
    e2 = estilo2.lower().strip() if estilo2 else 'casual'

    if e1 == e2:
        return True

    comp1 = COMPATIBILIDADE_ESTILOS.get(e1, ['casual'])
    return e2 in comp1


def sao_cores_harmonicas(cor1, cor2):
    c1 = cor1.lower().strip()
    c2 = cor2.lower().strip()

    if c1 == c2:
        return True

    combinacoes = COMBINACOES_CORES.get(c1, [])
    return c2 in combinacoes


def gerar_recomendacao_look(pecas, clima='Geral', ocasiao='Geral'):

    categorias_superiores = ['camiseta', 'blusa', 'camisa', 'casaco', 'jaqueta', 'top', 'moletom']
    categorias_inferiores = ['calça', 'short', 'bermuda', 'saia', 'calca']

    pecas_superiores = [p for p in pecas if p.categoria.lower().strip() in categorias_superiores]
    pecas_inferiores = [p for p in pecas if p.categoria.lower().strip() in categorias_inferiores]

    if not pecas_superiores or not pecas_inferiores:
        return None, "É necessário ter pelo menos uma peça superior e uma inferior cadastradas."

    if clima.lower() == 'verão':
        pecas_superiores = [p for p in pecas_superiores if
                            p.categoria.lower().strip() not in ['casaco', 'jaqueta', 'moletom']]
        pecas_inferiores = [p for p in pecas_inferiores if
                            p.categoria.lower().strip() in ['short', 'bermuda', 'saia']] or pecas_inferiores
    elif clima.lower() == 'inverno':
        pecas_inferiores = [p for p in pecas_inferiores if
                            p.categoria.lower().strip() not in ['short', 'bermuda']] or pecas_inferiores

    combinacoes_validas = []

    for sup in pecas_superiores:
        for inf in pecas_inferiores:
            cor_combina = sao_cores_harmonicas(sup.cor, inf.cor)
            estilo_combina = sao_estilos_compativeis(getattr(sup, 'estilo', ''), getattr(inf, 'estilo', ''))

            if cor_combina and estilo_combina:
                combinacoes_validas.append((sup, inf, "perfeita"))
            elif cor_combina:
                combinacoes_validas.append((sup, inf, "boa_cor"))
            elif estilo_combina:
                combinacoes_validas.append((sup, inf, "bom_estilo"))

    if combinacoes_validas:

        perfeitas = [pair for pair in combinacoes_validas if pair[2] == "perfeita"]
        if perfeitas:
            sup, inf, tipo = random.choice(perfeitas)
            descricao = (f"Look perfeito! A {sup.categoria} ({sup.cor}, estilo {sup.estilo or 'casual'}) "
                         f"harmoniza em cores e estilo com a {inf.categoria} ({inf.cor}, estilo {inf.estilo or 'casual'}).")
        else:
            sup, inf, tipo = random.choice(combinacoes_validas)
            descricao = (f"Sugestão de look: {sup.categoria} ({sup.cor}) combinada com {inf.categoria} ({inf.cor}).")
    else:
        sup = random.choice(pecas_superiores)
        inf = random.choice(pecas_inferiores)
        descricao = f"Combinação casual: {sup.categoria} ({sup.cor}) com {inf.categoria} ({inf.cor})."

    nome_look = f"Look {clima.capitalize()} - {sup.categoria.capitalize()} & {inf.categoria.capitalize()}"
    return (sup, inf), descricao, nome_look