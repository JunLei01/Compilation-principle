#include<iostream>
#include<stdio.h>
#include<string>
#include<string.h>
#include<vector>
#include<windows.h> 
#define KEY_MAX 24
#define SYMBOL 19
#define WORD_LENS 20 
using namespace std;
int Line_NO=1;

//声明关键字结构体 
typedef struct{
	string key;
	int token;
}keywords;
keywords kw[KEY_MAX];

//声明标识符 
string str[KEY_MAX]={"int","float","double","char","void","main","for",
	"if","else","do","while","return","break","struct","switch","case",
	"static","define","typedef","union","enum","const","long","short"};
//char symbol[SYMBOL]={")","[","]","{","}","+","-","*","/","%","=","<",
//	">","\""};
char symbol[SYMBOL]={'(', ')', '[', ']', '{', '}', '+', '-', '*', '/', '%', '=',
	'<', '>', '"', '#', ':', ';', ','};
string error[20];
int error_line[20]={0};
int lines=1;

 int color(int c)
 {
 	SetConsoleTextAttribute(GetStdHandle(STD_OUTPUT_HANDLE),c);
	return 0; 
 }

//初始化关键字结构体 
void key_words_init(){
	for(int i=0; i<KEY_MAX; i++){
		kw[i].key=str[i];
		kw[i].token=i+2;
	}
} 

//判定当前字符是否是字母 
bool is_letter(char a){
	if(((a>='a')&&(a<='z')) || ((a<='Z')&&(a>='A')))
		return true;
	else
		return false;
}

//判断当前字符是否是数字 
bool is_digit(char a){
	if((a>='0') && (a<='9'))
		return true;
	else
		return false;
}

//判断字符串是否是关键字 
int is_keyword(string str){
	for(int i=0; i<KEY_MAX; i++){
		if(kw[i].key==str)
			return kw[i].token;
	}
	return 0;
}

//判断当前字符是否是符号（单目） 
int is_symbol1(char a){
	for(int i=0; i<SYMBOL; i++){
		if(symbol[i]==a)
			return i+26;
	}
	return 0;
}

//判断当前字符是否是符号（双目） 
int is_symbol2(char a, char b){
	switch(a){
		case '=':
			if(b=='=')
				return 45;
		case '!':
			if(b=='=')
				return 46;
		case '&':
			if(b=='$')
				return 47;
		case '|':
			if(b=='|')
				return 48;
		case '+':
			if(b=='+')
				return 49;
			else if(b=='=')
				return 51;
		case '-':
			if(b=='-')
				return 50;
			else if(b=='=')
				return 52;
		case '>':
			if(b=='=')
				return 53;
		case '<':
			if(b=='=')
				return 54;
		default:
			return 0;
	}
}

//判断变量命名是否合法 
int is_variable_legal(string str, int line){
	int flag=0;
	str=(str+'\0').c_str();
	string::iterator sit=str.begin();
	while(sit!=str.end()){
		flag=is_symbol1(*sit);
		sit++;
	}
	if(is_digit(str.at(0))){
		error[lines]=(str+"   Variable naming is illegal").c_str();
		error_line[lines]=line;
	}
	return 0;
}

//判断数字是否合法 
int is_number_legal(string str, int line){
	int flag=0;
	int E=0;
	int point=0;
	string::iterator sit=str.begin();
	while(sit!=str.end()){
		if(*sit=='.')
			flag++;
		if(*sit=='E' || *sit=='e')
			E++;
		if(E==1 && *sit=='.' && flag>1 && point==0){
			flag=1;
			point=1;
		}
		sit++;
	}
	if(flag>1 || E>1){
		error[lines]=(str+"    Number is illegal").c_str();
		error_line[lines]=line;
	}
}

//词法分析函数 
void lexical_analysis(FILE * fp){
	char ch;
	string words;
	words="";
	while((ch=fgetc(fp))!=EOF){
		if(ch==' ' || ch=='\t')
			continue;
		else if(ch=='\n')
			Line_NO++;
			
		//关键字判断 
		else if(is_letter(ch)){
 			words = "";
			while(is_letter(ch) || is_digit(ch) || ch=='_'){
				words=(words+ch).c_str();
				ch=fgetc(fp);
			}
			int value=is_keyword(words);
			if(value)
				printf("<%s,%d>\n", words.c_str(), value);
				//cout<<"<"<<words<<","<<value<<">"<<endl;
			else
				printf("<%s,1>\n", words.c_str());
				
			fseek(fp,-1L,SEEK_CUR);
		}
		
		//数字判断
		else if(is_digit(ch)){
			words = "";
			words=(words+ch).c_str();
			if(is_letter((ch=fgetc(fp)))){
				
				while(is_letter(ch) || is_digit(ch) || ch=='_'){
				words=(words+ch).c_str();
				ch=fgetc(fp);
				}
				is_variable_legal(words, Line_NO);
				printf("<%s,1>\n", words.c_str());
				fseek(fp,-1L,SEEK_CUR);
			}
			
			else {
				while(is_digit(ch) || ch=='.' || ch=='E' || ch=='e' || ch=='-' || ch=='+'){
					words=(words+ch).c_str();
					ch=fgetc(fp);
				}
				is_number_legal(words, Line_NO);
				printf("<%s,1>\n", words.c_str());
				fseek(fp,-1L,SEEK_CUR);
			}
			
		} 
		//符号判断 
		else{
			char temp;
			temp=ch;
			ch=fgetc(fp);
			
			//判断是否是注释 
			if(temp=='/'){
				if(ch=='/'){
					while(ch!='\n')
						ch=fgetc(fp);
				}
				if(ch=='*'){
					char end=' ';
					while(ch!='*' && end!='/' && ch!=EOF){
						ch=fgetc(fp);
						if(ch=='*')
							end=fgetc(fp);
						if(ch==EOF){
							cout<<"The file is analyzed!"<<endl;
							break;	
						}
					}	
				}
				else
					cout<<"<"<<temp<<","<<"55"<<">"<<endl;
				fseek(fp,-1L,SEEK_CUR);
			} 
				
			if(is_letter(ch) || is_digit(ch) || ch!=' ' || ch=='\t'){
				int value=is_symbol1(temp);
				if(value!=0)
					printf("<%c,%d>\n", temp, value);
			}
			else{
				int value=is_symbol2(temp, ch);
				if(value!=0)
					printf("<%c%c,%d>\n", temp, ch, value);
			}
			if(ch==EOF)
				break;
			fseek(fp,-1L,SEEK_CUR);
		}		
	}
}

//输出报错信息 
void error_detect(){
	if(error_line[1]==0){
		color(12); 
		printf("0 warnning, 0 error!"); 
	} 
	else{
		printf("\nError:\n");
		color(12); 
		for(int i=1; i<2; i++)
		printf("line[%d]:  %s\n", error_line[i], error[i].c_str());
	}

}

int main(){
	char input[20];
	FILE *fpin=NULL;
	cout<<"Please enter your program:"<<endl;
	cin>>input;
	fpin=fopen(input, "r");
	key_words_init();
	lexical_analysis(fpin);
	error_detect();
	fclose(fpin);
	return 0;
}
