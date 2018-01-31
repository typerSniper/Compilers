void main ()
{
	int a, *q;
    q= &a;
    **&(&(*q)) = 0;
}