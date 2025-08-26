#include <stdio.h> 
#include <stdlib.h>  
#include <string.h>
#include <unistd.h>   
#include <arpa/inet.h> 
#include <errno.h>    
#include <netdb.h> 
#define DEFAULT_PORT 2000

int main(int argc, char *argv[]) {
    int sock; 
    struct sockaddr_in server; 
    struct hostent* hp; 

    if (argc < 3) {
        printf("Usage: %s hostname port\n", argv[0]); 
        exit(1); 
    }

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Opening stream socket"); 
        exit(1); 
    }

    hp = gethostbyname(argv[1]);
    if (hp == NULL) {
        fprintf(stderr, "%s: unknown host\n", argv[1]); 
        exit(2); 
    }

    server.sin_family = AF_INET; 
    memcpy((char*)&server.sin_addr, (char*)hp->h_addr, hp->h_length); 
    server.sin_port = htons(atoi(argv[2])); 

    if (connect(sock, (struct sockaddr*)&server, sizeof(server)) == -1) {
        perror("Connecting stream socket"); 
        exit(1); 
    } else {
        printf("Connection successful\n\n"); 
    }

    {
        char recvbuf[2048];
        memset(recvbuf, 0, sizeof(recvbuf));
        ssize_t r = recv(sock, recvbuf, sizeof(recvbuf) - 1, 0);
        if (r > 0) {
            recvbuf[r] = '\0';
            printf("%s", recvbuf);
        } else if (r == 0) {
            printf("Server closed connection immediately.\n");
            close(sock);
            return 0;
        } else {
            perror("recv (initial)");
            close(sock);
            return 1;
        }
    }

    while (1) {
        char line[1024];
        if (!fgets(line, sizeof(line), stdin)) {
            break;
        }

        ssize_t len = strlen(line);
        if (send(sock, line, len, 0) < 0) {
            perror("send");
            break;
        }
        {
            char recvbuf[2048];
            memset(recvbuf, 0, sizeof(recvbuf));
            ssize_t r = recv(sock, recvbuf, sizeof(recvbuf) - 1, 0);
            if (r > 0) {
                recvbuf[r] = '\0';
                printf("%s", recvbuf);
            } else if (r == 0) {
                printf("Server closed connection.\n");
                break;
            } else {
                perror("recv");
                break;
            }
        }

        if (line[0] == 'q' && (line[1] == '\n' || line[1] == '\0')) {
            printf("Exiting client.\n");
            break;
        }
    }

    close(sock);
    return 0;
}
