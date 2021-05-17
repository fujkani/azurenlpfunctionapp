# As-build documentation

Note: some of the instructions below are OS-specific, i.e. in my case MacOS

- Upgrade Azure Client to latest version or you may face issues further below
brew upgrade azure-cli

- Login to the account
az login

A listing of available consumption locations: We are choosing westeaurope below
az functionapp list-consumption-locations

- MacOS: install Homebrew then

brew tap azure/functions
brew install azure-functions-core-tools@3

if upgrading on a machine that has azure cli 2.x installed
brew link --overwrite azure-functions-core-tools@3


- Create the Azure Function App: (assumes resource group and storage are already created)

export AZURE_STORAGE_ACCOUNT=nlp1storage
functionAppName=NLPFunctionApp
region=westeurope
pythonVersion=3.7 #3.6 also supported
shareName=nlpshare
directoryName=nlpdata
shareId=nlpdatashare
mountPath=/nlp
resourceGroup=nlp_Ressource_Group
export AZURE_STORAGE_KEY=$(az storage account keys list -g $resourceGroup -n $AZURE_STORAGE_ACCOUNT --query '[0].value' -o tsv)


az functionapp create \
  --name $functionAppName \
  --storage-account $AZURE_STORAGE_ACCOUNT \
  --consumption-plan-location $region \
  --resource-group nlp_Ressource_Group \
  --os-type Linux \
  --runtime python \
  --runtime-version $pythonVersion \
  --functions-version 3


# Create a share in Azure Files.
az storage share create \
  --name $shareName 

# Create a directory in the share.
az storage directory create \
  --share-name $shareName \
  --name $directoryName

# Add the share to the app
az webapp config storage-account add \
  --resource-group nlp_Ressource_Group \
  --name $functionAppName \
  --custom-id $shareId \
  --storage-type AzureFiles \
  --share-name $shareName \
  --account-name $AZURE_STORAGE_ACCOUNT \
  --mount-path $mountPath \
  --access-key $AZURE_STORAGE_KEY

az webapp config storage-account list \
  --resource-group nlp_Ressource_Group \
  --name $functionAppName
  

# Set app settings i.e. environment variables, available accross all functions

  --- Set Application settings in Azure for each app (these should be also defined in local.settings.json for local runs)

functionAppName=NLPFunctionApp

az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings NLTK_PATH="/nlp/nlpdata/nltk/nltk_data"

az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings SENTRY_DSN="your sentry dsn here"

az functionapp config appsettings set --name $functionAppName --resource-group $resourceGroup --settings AZURE_FUNCTIONS_ENVIRONMENT="Production"



//Create function project
python -m venv .venv
func init NLPFunctionProject --python

//Create first function
func new --name NLPParseResume --template "HTTP trigger" --authlevel "anonymous"
func new --name shared_code --template "HTTP trigger" --authlevel "anonymous"
mkdir tests


Note: Remember to maintain app new settings in local.settings.json as in azure
