# Ralo Oculto Inteligente V1 — Autodesk Fusion

Este pacote contém um **script gerador para o Autodesk Fusion**. Ao executá-lo, o Fusion cria um projeto nativo com corpos BRep editáveis.

## O que o arquivo cria

- Tampa de 900 mm dividida em **3 módulos imprimíveis**.
- Ranhuras de escoamento.
- Trilhos laterais, longarina central e nervuras transversais.
- Encaixes macho/fêmea entre os módulos.
- Pequenas saliências antiderrapantes.
- Três cartuchos removíveis tipo pente para estudar a retenção de cabelo.
- Um **cupom estrutural de 100 mm**, separado do conjunto, para imprimir primeiro.

## Como abrir no Fusion

1. Descompacte o ZIP sem alterar o nome da pasta `RaloOcultoV1`.
2. Abra o Autodesk Fusion no computador.
3. Vá em **Utilities > Scripts and Add-Ins**.
4. Na aba **Scripts**, use o botão `+` para adicionar a pasta `RaloOcultoV1`.
5. Selecione `RaloOcultoV1` e clique em **Run**.
6. O projeto será criado em um documento novo. Salve-o normalmente como projeto Fusion/F3D.

## Dimensões iniciais

- Comprimento total: 900 mm.
- Largura: 78 mm.
- Três módulos de aproximadamente 299,3 mm.
- Tampa: 5,5 mm.
- Reforços inferiores: 8 mm.
- Ranhuras: 3,2 × 28 mm.

Essas dimensões são **apenas um ponto de partida**. Meça com paquímetro:

- comprimento e largura úteis;
- profundidade disponível;
- largura das bordas de apoio;
- localização do furo de saída;
- folgas necessárias para tirar e recolocar a tampa.

Edite as constantes no início de `RaloOcultoV1.py` e execute novamente.

## Ensaio recomendado

Imprima primeiro somente o corpo chamado `CUPOM_TESTE_ESTRUTURAL_100mm`.

Faça ensaios progressivos em uma bancada, com carga distribuída e uma proteção por baixo. Observe:

- flexão permanente;
- trincas entre linhas;
- delaminação;
- quebra perto das ranhuras;
- deformação das linguetas.

**Não pise no conjunto instalado apenas porque o modelo parece rígido.** O arquivo não foi validado por cálculo estrutural, ensaio físico ou certificação. PLA também pode sofrer fluência, deformação térmica e degradação de desempenho no uso real do banheiro.

## Organização dos corpos

- `Tampa_01`, `Tampa_02`, `Tampa_03`: módulos estruturais.
- `Filtro_Pente_01`, `Filtro_Pente_02`, `Filtro_Pente_03`: conceito de cartucho removível, mostrado abaixo da tampa em posição explodida.
- `CUPOM_TESTE_ESTRUTURAL_100mm`: peça curta para validação.

## Limitação importante

O projeto é criado como **modelagem direta**, escolhida para tornar o gerador mais robusto. As dimensões são controladas pelas constantes do script; alterar valores no script e executá-lo novamente recria a versão atualizada. Depois disso, você pode usar as ferramentas normais do Fusion para refinar os corpos.
