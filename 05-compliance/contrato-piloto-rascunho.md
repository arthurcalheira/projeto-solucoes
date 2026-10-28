# Rascunho: contrato de piloto do PREV01

> ⚠️ **Rascunho para discussão, não é documento jurídico pronto.** Antes de
> assinar, um advogado precisa revisar, de preferência com experiência em
> contratos de tecnologia e LGPD. Os campos `{{...}}` são preenchidos para
> cada escritório.

---

**CONTRATO DE PRESTAÇÃO DE SERVIÇOS: PILOTO DE ATENDIMENTO AUTOMATIZADO**

**CONTRATADA:** {{RAZÃO SOCIAL DA SUA EMPRESA}}, CNPJ {{CNPJ}}, com sede em
{{ENDEREÇO}}.

**CONTRATANTE:** {{RAZÃO SOCIAL DO ESCRITÓRIO}}, CNPJ {{CNPJ}}, com sede em
{{ENDEREÇO}}, representada por {{NOME E OAB}}.

### 1. Objeto

1.1. Piloto de **{{30}} dias** do serviço de atendimento e triagem automatizados
pelo WhatsApp (PREV01). O serviço inclui: configuração, integração com o
número do CONTRATANTE, painel de acompanhamento, avisos à equipe,
treinamento ({{1}} sessão) e suporte em horário comercial.

1.2. Não estão incluídos: análise jurídica, cálculo de benefícios, anúncios e
atendimento a clientes com processo em andamento.

### 2. Natureza do serviço e responsabilidade técnica

2.1. O serviço **coleta e organiza informações e documentos**. Ele **não
presta consultoria jurídica**, não avalia direito a benefício e não promete
resultado.

2.2. Toda análise, orientação jurídica e decisão sobre o caso são de
responsabilidade exclusiva dos advogados do CONTRATANTE.

2.3. O CONTRATANTE revisa e aprova o roteiro de triagem e os textos usados
pelo assistente, inclusive para conferir a conformidade com as normas de
publicidade da OAB.

### 3. Prazo e implantação

3.1. A implantação começa na assinatura. O piloto começa quando o assistente
for ligado no número do CONTRATANTE, previsto para {{DATA}}, e dura {{30}}
dias.

3.2. Atrasos causados por terceiros (por exemplo, a verificação da empresa
pela Meta) ou pela falta de informações do CONTRATANTE prorrogam o início
sem multa.

### 4. Preço e pagamento

4.1. Valor do piloto: **R$ {{1.500,00}}**, pago {{à vista / 50% na assinatura e
50% no início}}.

4.2. Se o CONTRATANTE contratar o serviço mensal em até {{15}} dias após o
fim do piloto, o valor do piloto é abatido da taxa de implantação.

4.3. Os custos de uso da IA e das mensagens do WhatsApp durante o piloto
estão incluídos até {{300}} conversas. O excedente é cobrado a R$ {{X}} por
conversa, mediante aviso prévio.

### 5. Proteção de dados (LGPD)

5.1. O CONTRATANTE é o **controlador** dos dados pessoais dos seus clientes e
potenciais clientes. A CONTRATADA é **operadora** e trata os dados apenas
para prestar o serviço, conforme as instruções do CONTRATANTE.

5.2. A CONTRATADA se compromete a:
a) usar os dados só para este serviço, sem uso próprio nem venda;
b) manter medidas de segurança adequadas: acesso restrito, senhas, conexão
criptografada e backups protegidos;
c) usar como suboperadores apenas os listados no Anexo I (por exemplo, o
provedor do modelo de IA, a Meta/WhatsApp e o provedor de hospedagem), em
condições que não permitam o uso dos dados para treinar modelos;
d) comunicar ao CONTRATANTE qualquer incidente de segurança em até {{48}}
horas depois de tomar conhecimento;
e) atender pedidos de titulares encaminhados pelo CONTRATANTE, inclusive de
exclusão;
f) ao fim do contrato, devolver ou apagar os dados em até {{30}} dias,
conforme o CONTRATANTE escolher.

5.3. Os dados de saúde (laudos, atestados) são dados sensíveis e recebem o
mesmo tratamento, com acesso restrito à equipe indicada pelo CONTRATANTE.

### 6. Confidencialidade

6.1. As partes mantêm sigilo sobre as informações recebidas, inclusive após
o fim do contrato, respeitado o sigilo profissional do advogado.

### 7. Propriedade

7.1. Os roteiros, os modelos e as informações do CONTRATANTE pertencem ao
CONTRATANTE.

7.2. O software, os prompts genéricos e o painel pertencem à CONTRATADA. O
CONTRATANTE recebe licença de uso durante a vigência.

### 8. Limitação de responsabilidade

8.1. A CONTRATADA não responde por decisões jurídicas do CONTRATANTE nem por
indisponibilidade de serviços de terceiros (WhatsApp, provedores de IA e de
hospedagem). Ela deve, porém, agir para restabelecer o serviço e avisar o
CONTRATANTE.

8.2. A responsabilidade total da CONTRATADA neste piloto fica limitada ao
valor pago pelo piloto, salvo em caso de dolo ou de violação da cláusula 5.

### 9. Encerramento

9.1. Ao fim do piloto, o contrato termina, salvo contratação do serviço
mensal.

9.2. Qualquer parte pode encerrar antes, com aviso de {{7}} dias. Os valores
são proporcionais ao período utilizado.

### 10. Foro

10.1. Fica eleito o foro de {{CIDADE/UF}}.

{{LOCAL}}, {{DATA}}.

_____________________________ CONTRATADA
_____________________________ CONTRATANTE

---

**Anexo I: Suboperadores**

| Fornecedor | Uso | Dados tratados |
|---|---|---|
| Anthropic (API do Claude) | Conversa e leitura de documentos | Mensagens e documentos enviados pelo cliente |
| Meta (WhatsApp Business Platform) | Envio e recebimento de mensagens | Telefone, nome do perfil, mensagens e arquivos |
| {{Provedor de hospedagem}} | Servidor, banco e arquivos | Todos os dados do atendimento |
| {{Provedor de e-mail}} | Avisos à equipe | Nome, assunto e link do caso |
