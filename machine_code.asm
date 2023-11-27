0000000000001169 <main>:
    1169:	f3 0f 1e fa          	endbr64 
    116d:	55                   	push   %rbp
    116e:	48 89 e5             	mov    %rsp,%rbp
    1171:	c7 45 fc 01 00 00 00 	movl   $0x1,-0x4(%rbp)
    1178:	c6 45 fb 01          	movb   $0x1,-0x5(%rbp)
    117c:	0f b6 45 fb          	movzbl -0x5(%rbp),%eax
    1180:	89 45 fc             	mov    %eax,-0x4(%rbp)
    1183:	b8 00 00 00 00       	mov    $0x0,%eax
    1188:	5d                   	pop    %rbp
    1189:	c3                   	ret    

